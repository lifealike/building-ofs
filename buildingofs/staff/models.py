from buildingofs.utils import models

from . import managers


class PermissionsMixin(object):

    def has_perm(self, perm):
        return perm in self.permissions

    def has_any_perm(self, perms):
        return bool(set(perms).intersection(self.permissions))

    def has_perms(self, perms):
        return bool(set(perms).issubset(self.permissions))


class Staff(models.RPCModel, PermissionsMixin):

    class Meta:
        verbose_name_plural = "Staff Members"
        verbose_name = "Staff Member"

    objects = managers.StaffManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []  # a hack to get django's default Auth to work. Perhaps rewrite auth custom and get rid of this?

    id = models.IntegerField(primary_key=True, sortable=True, verbose_name="ID")
    employee_number = models.IntegerField(sortable=True, blank=True, null=True)
    username = models.CharField(max_length=50, unique=True, sortable=True, blank=True)
    primary_email_address = models.EmailField(max_length=255, verbose_name="Primary Email", blank=True)
    password = models.CharField(max_length=128)
    is_enabled = models.BooleanField(default=True, verbose_name="Enabled")

    first_name = models.TextField(sortable=True)
    last_name = models.TextField(sortable=True)
    full_name = models.TextField()

    job_title = models.TextField(sortable=True)
    photo_asset_id = models.TextField(blank=True, null=True)

    @property
    def permissions(self):
        if not hasattr(self, '_permissions'):
            try:
                self._permissions = self._extra_data['all_permission_codes']
            except (AttributeError, KeyError):
                self._permissions = []
        return self._permissions

    @property
    def is_active(self):
        return self.is_enabled

    @is_active.setter
    def is_active(self, value):
        self.is_enabled = value

    def is_authenticated(self):
        return True

    def refresh(self):
        data = self.__class__.objects.get(id=self.id)
        return self.__class__(data.__dict__)

    def __unicode__(self):
        return ' '.join([self.first_name, self.last_name])
