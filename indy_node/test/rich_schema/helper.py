# Sets the named attribute on the given object to the specified value inside the scope.
class ModifiedAttributeScope:
    def __init__(self, obj, attr, new_value):
        self._obj = obj
        self._attr = attr
        self._new_value = new_value

    def __enter__(self):
        self._old_value = getattr(self._obj, self._attr)
        setattr(self._obj, self._attr, self._new_value)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        setattr(self._obj, self._attr, self._old_value)


# Returns context with RichSchemas feature enabled.
def rich_schemas_enabled_scope(tconf):
    return ModifiedAttributeScope(tconf, "enableRichSchemas", True)
