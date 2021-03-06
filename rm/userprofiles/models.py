"""
Metadating on Randomise Me users
"""
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.db import models

class RMUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=RMUserManager.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(
            email,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user



class RMUser(AbstractBaseUser):
    """
    The Profile of a RM user
    """
    STANDARD = 'st'
    ADVANCED = 'ad'
    PREMIUM  = 'pr'
    ACCOUNT_CHOICES = (
        (STANDARD, 'Standard'),
        (ADVANCED, 'Advanced'),
        (PREMIUM,  'Premium')
        )

    MALE   = 'ma'
    FEMALE = 'fe'
    GENDERS = (
        (MALE,   'Male'),
        (FEMALE, 'Female')
        )

    QUESTION_LONG = "Receive Questions"
    QUESTION_HELP = """
If you elect to receive questions, then participants in your trials can use
Randomise Me to send you questions about your trial. You'll receive questions
by email.
"""
    FORM_LONG = "1 Page Create Trial"
    FORM_HELP = """
If you elect to use the 1 page create trial view, then you will see all
steps that comprise creating a trial on a single page
"""
    EMAIL_LONG = "Get emails from Randomise Me"
    EMAIL_HELP = """
If you don't want to get emails from Randomise Me untick this box and we
won't send you any more.
"""


    username      = models.CharField(max_length=40, unique=True, db_index=True)
    email         = models.EmailField(max_length=254, unique=True)
    account       = models.CharField(max_length=2, choices=ACCOUNT_CHOICES, default='st')
    is_active     = models.BooleanField(default=True)
    is_staff      = models.BooleanField(default=False)
    is_superuser  = models.BooleanField(default=False)
    name          = models.CharField(max_length=200, blank=True, null=True)
    dob           = models.DateField(blank=True, null=True, help_text="Your date of birth")
    gender        = models.CharField(max_length=2, blank=True, null=True, choices=GENDERS)
    postcode      = models.CharField(max_length=20, blank=True, null=True)
    receive_questions = models.BooleanField(QUESTION_LONG, default=True,
                                            help_text=QUESTION_HELP)
    receive_emails = models.BooleanField(EMAIL_LONG, default=True, help_text=EMAIL_HELP)
    single_page = models.BooleanField(FORM_LONG, default=False, help_text=FORM_HELP)

    objects = RMUserManager()

    USERNAME_FIELD = 'email'
#    USERNAME_FIELD = 'username'

    def __unicode__(self):
        return self.email

    def get_full_name(self):
        # For this case we return email. Could also be User.first_name User.last_name if you have these fields
        return self.email

    def get_short_name(self):
        # For this case we return email. Could also be User.first_name if you have this field
        return self.email

    def __unicode__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        # Handle whether the user has a specific permission?"
        return True

    def has_module_perms(self, app_label):
        # Handle whether the user has permissions to view the app `app_label`?"
        return True

    @property
    def is_standard(self):
        """
        Predicate property to determine whether this user has
        a standard account.

        Return: bool
        Exceptions: None
        """
        return self.account == self.STANDARD

    def upgrade(self):
        """
        Upgrade our user please

        Return: None
        Exceptions: None
        """
        if self.is_standard:
            self.account = self.ADVANCED
            self.save()
        return

    def send_message(self, message):
        """
        Given a letter.Letter subclass representing our email,
        send the message.

        This api allows us to respect user preferences re. us
        not spamming them

        Arguments:
        - `message`: letter.Letter

        Return: none
        Exceptions: none
        """
        if self.receive_emails:
            message.send()
