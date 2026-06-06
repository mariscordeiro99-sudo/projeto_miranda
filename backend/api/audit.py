def record_audit_log(actor, action, target=None, metadata=None):
    from .models import AuditLog

    actor_user = actor if getattr(actor, 'is_authenticated', False) else None
    target_type = ''
    target_id = ''
    target_repr = ''

    if target is not None:
        target_type = target.__class__.__name__
        target_id = str(getattr(target, 'pk', '') or '')
        target_repr = str(target)[:255]

    return AuditLog.objects.create(
        actor=actor_user,
        actor_username=actor_user.get_username() if actor_user else '',
        action=action,
        target_type=target_type,
        target_id=target_id,
        target_repr=target_repr,
        metadata=metadata or {},
    )
