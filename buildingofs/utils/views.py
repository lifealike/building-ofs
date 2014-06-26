from braces.views import MultiplePermissionsRequiredMixin


class PermissionsMixin(MultiplePermissionsRequiredMixin):
    """ A subclass of MultiplePermissionsRequiredMixin that allows an "all"
    tuple to be assigned to any HTTP method (POST, GET, PUT, etc). This mixin
    also changes the default behaviour of self.raise_exception to always raise
    unless it's set to False """

    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        self._check_permissions_attr()

        if request.method in self.permissions:
            perms = self.permissions[request.method]
            self._check_perms_keys("all", perms)
            if perms:
                if not request.user.has_perms(perms):
                    if self.raise_exception:
                        raise PermissionDenied
                    return redirect_to_login(request.get_full_path(),
                                             self.get_login_url(),
                                             self.get_redirect_field_name())

        if len(self.permissions.get('any')) == 0:
            return super(MultiplePermissionsRequiredMixin, self).dispatch(request, *args, **kwargs)

        return super(PermissionsMixin, self).dispatch(request, *args, **kwargs)
