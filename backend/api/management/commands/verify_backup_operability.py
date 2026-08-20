import json

from django.core.management.base import BaseCommand

from api.backup import (
    build_backup_operational_status,
    record_backup_operational_evidence,
)


class Command(BaseCommand):
    help = 'Verifica a política operacional de backup e, opcionalmente, registra evidência em auditoria.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--record',
            action='store_true',
            help='Registra a verificação em AuditLog como evidência operacional.',
        )
        parser.add_argument(
            '--json',
            action='store_true',
            help='Exibe a saída em JSON.',
        )

    def handle(self, *args, **options):
        if options['record']:
            result = record_backup_operational_evidence()
        else:
            result = build_backup_operational_status()

        if options['json']:
            self.stdout.write(json.dumps(result, ensure_ascii=False, indent=2, default=str))
            return

        self.stdout.write(f"Status: {result['status']}")

        policy = result.get('policy', {})
        self.stdout.write('Política:')
        for key, value in policy.items():
            self.stdout.write(f'  - {key}: {value or "-"}')

        self.stdout.write('Checks:')
        for key, check in result.get('checks', {}).items():
            self.stdout.write(f"  - {key}: {check['status']} - {check['detail']}")

        audit_log_id = result.get('audit_log_id')
        if audit_log_id:
            self.stdout.write(f'Evidência registrada no AuditLog #{audit_log_id}.')
