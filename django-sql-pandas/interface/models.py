from django.db import models
from .psqli import DataBaseConnector, DataFrameMaker
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from testproject.settings import CIPHER_KEY # is absent, generate your own

key = CIPHER_KEY
cipher = Fernet(key)
now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
minus_day = datetime.now() - timedelta(days=1)
now_minus_day = minus_day.strftime('%Y-%m-%d %H:%M:%S')


class Profile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )
    # name = models.CharField(max_length=50, blank=True)
    # reg_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


class DataBaseModel(models.Model):
    """
    Creating database record, establishing connection.
    Encrypting password to store it openly in django
    """
    # relation
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE
    )
    # attributes
    db_name = models.CharField(max_length=50)
    db_address = models.CharField(max_length=20)
    db_user = models.CharField(max_length=20)
    db_psswd = models.CharField(max_length=50)
    sql_name = models.CharField(max_length=20)

    # methods
    def connect(self):
        dc = DataBaseConnector()
        db = dc.connect_db(
            self.db_address,
            self.db_user,
            self.bytes_decode(),
            self.sql_name
        )
        return db

    def __str__(self):
        return self.db_name

    # method used to store encrypted db password  in django
    @staticmethod
    def encrypt(string):
        encrypted_string = cipher.encrypt(bytes(string, encoding='utf-8'))
        return encrypted_string

    # method used to decrypt password before connection
    @staticmethod
    def decrypt(encrypted_string):
        decrypted_string = cipher.decrypt(encrypted_string)
        return decrypted_string.decode('utf-8')

    # method used to store encrypted password in str format
    def save(self, *args, **kwargs):
        self.db_psswd = str(self.encrypt(self.db_psswd), 'utf-8')
        super().save(*args, **kwargs)

    # method used to decode decrypted password before connection
    def bytes_decode(self):
        de = bytes(self.db_psswd, 'utf-8')
        # print(de)
        de = self.decrypt(de)
        # print(de)
        return de


class NodeModel(models.Model):
    """Contains parameters to pass to PSQLInterface"""
    # relation
    data_base = models.ForeignKey(DataBaseModel, on_delete=models.CASCADE)
    # attributes
    node_id = models.CharField(max_length=20)
    time_from = models.CharField(max_length=50, default=now_minus_day)
    time_to = models.CharField(max_length=50, default=now)

    # methods
    def test_connect(self):
        """Connect to related FK database model o establish connection"""
        return self.data_base.connect()

    """Data retrieval methods"""
    def frame_nunique(self):
        """Retrieve non-unique messages"""
        data = DataFrameMaker(
            self.test_connect(),
            self.node_id,
            self.time_from,
            self.time_to
        ).get_nunique_messages()
        return data

    def frame_log(self):
        """Retrieve whole log as is"""
        data = DataFrameMaker(
            self.test_connect(),
            self.node_id,
            self.time_from,
            self.time_to
        ).get_log()
        return data

    def frame_plot(self):
        """Retrieve simple *time-to-messages number* relation plot """
        graphic = DataFrameMaker(
            self.test_connect(),
            self.node_id,
            self.time_from,
            self.time_to
        ).get_plot()
        return graphic

    def last_messages(self):
        """Retrieve last 5 messages"""
        messages_last = DataFrameMaker(
            self.test_connect(),
            self.node_id,
            self.time_from,
            self.time_to
        ).get_last_messages()
        return messages_last

    def __str__(self):
        return self.node_id
