from datetime import datetime, time, timedelta

from django.conf import settings
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime

from .audit import record_audit_log
from .models import AuditLog


BACKUP_EVIDENCE_ACTION = 'backup_operational_evidence'


def build_backup_operational_status(now=None, include_evidence=True):
    now = now or timezone.now()
    checks = {
        'provider': check_backup_provider(),
        'frequency': check_backup_frequency(),
        'retention': check_backup_retention(),
        'restore_test': check_restore_test(now),
        'database_ssl': check_database_ssl(),
    }

    if include_evidence:
        checks['latest_evidence'] = check_latest_evidence(now)

    status = summarize_backup_checks(checks)
    return {
        'status': status,
        'policy': backup_policy_snapshot(),
        'checks': checks,
    }


def record_backup_operational_evidence(actor=None):
    result = build_backup_operational_status(include_evidence=False)
    metadata = {
        'status': result['status'],
        'policy': result['policy'],
        'checks': result['checks'],
        'recorded_at': timezone.now().isoformat(),
    }
    audit_log = record_audit_log(
        actor,
        BACKUP_EVIDENCE_ACTION,
        metadata=metadata,
    )
    return {
        'audit_log_id': audit_log.id,
        **metadata,
    }


def backup_policy_snapshot():
    return {
        'provider': settings.BACKUP_PROVIDER,
        'frequency_hours': settings.BACKUP_FREQUENCY_HOURS,
        'retention_days': settings.BACKUP_RETENTION_DAYS,
        'min_retention_days': settings.BACKUP_MIN_RETENTION_DAYS,
        'restore_test_interval_days': settings.BACKUP_RESTORE_TEST_INTERVAL_DAYS,
        'last_restore_test_at': settings.BACKUP_LAST_RESTORE_TEST_AT,
        'evidence_url': settings.BACKUP_EVIDENCE_URL,
    }


def check_backup_provider():
    provider = settings.BACKUP_PROVIDER.strip()
    if not provider:
        return degraded('BACKUP_PROVIDER não foi configurado.')
    return healthy(f'Provedor de backup declarado: {provider}.')


def check_backup_frequency():
    frequency_hours = settings.BACKUP_FREQUENCY_HOURS
    if frequency_hours <= 0:
        return degraded('BACKUP_FREQUENCY_HOURS deve ser maior que zero.')
    if frequency_hours > 24:
        return degraded('Frequência configurada acima de 24 horas.')
    return healthy('Frequência configurada para backup diário ou melhor.')


def check_backup_retention():
    retention_days = settings.BACKUP_RETENTION_DAYS
    min_retention_days = settings.BACKUP_MIN_RETENTION_DAYS
    if retention_days < min_retention_days:
        return degraded(
            f'Retenção de {retention_days} dias abaixo do mínimo de {min_retention_days} dias.'
        )
    return healthy(f'Retenção configurada para {retention_days} dias.')


def check_restore_test(now):
    last_restore_test = parse_configured_datetime(settings.BACKUP_LAST_RESTORE_TEST_AT)
    if not last_restore_test:
        return degraded('BACKUP_LAST_RESTORE_TEST_AT não foi configurado.')

    max_age = timedelta(days=settings.BACKUP_RESTORE_TEST_INTERVAL_DAYS)
    age = now - last_restore_test
    if age < timedelta(0):
        return degraded('BACKUP_LAST_RESTORE_TEST_AT está no futuro.')
    if age > max_age:
        return degraded('Último teste de restauração está fora do intervalo permitido.')

    return healthy('Teste de restauração recente registrado.', age_days=age.days)


def check_database_ssl():
    database = settings.DATABASES.get('default', {})
    engine = database.get('ENGINE', '')
    if 'mysql' not in engine:
        return degraded('Banco padrão não usa MySQL/Aiven neste ambiente.')

    if not settings.DB_SSL_REQUIRED:
        return degraded('DB_SSL_REQUIRED está desativado.')

    ssl_options = database.get('OPTIONS', {}).get('ssl')
    if ssl_options is None:
        return degraded('Banco MySQL sem opções SSL configuradas.')

    return healthy('Banco MySQL configurado com SSL obrigatório.')


def check_latest_evidence(now):
    latest_log = (
        AuditLog.objects
        .filter(action=BACKUP_EVIDENCE_ACTION)
        .order_by('-created_at')
        .first()
    )
    if not latest_log:
        return degraded('Nenhuma evidência operacional de backup foi registrada.')

    max_age = timedelta(hours=settings.BACKUP_FREQUENCY_HOURS + 1)
    age = now - latest_log.created_at
    if age > max_age:
        return degraded('Última evidência operacional de backup está vencida.')

    return healthy(
        'Evidência operacional recente encontrada.',
        audit_log_id=latest_log.id,
        recorded_at=latest_log.created_at.isoformat(),
    )


def parse_configured_datetime(value):
    if not value:
        return None

    parsed = parse_datetime(value)
    if parsed is None:
        parsed_date = parse_date(value)
        if parsed_date:
            parsed = datetime.combine(parsed_date, time.min)

    if parsed is None:
        return None

    if timezone.is_naive(parsed):
        return timezone.make_aware(parsed, timezone.get_current_timezone())
    return parsed


def summarize_backup_checks(checks):
    statuses = {check['status'] for check in checks.values()}
    if 'unhealthy' in statuses:
        return 'unhealthy'
    if 'degraded' in statuses:
        return 'degraded'
    return 'healthy'


def healthy(detail, **extra):
    return {'status': 'healthy', 'detail': detail, **extra}


def degraded(detail, **extra):
    return {'status': 'degraded', 'detail': detail, **extra}
