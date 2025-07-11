from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        
        # Set username to email if not provided
        if 'username' not in extra_fields:
            extra_fields['username'] = email.split('@')[0]
            
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


    # For super user
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser = True")
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff = True")
        
        if extra_fields.get('is_active') is not True:
            raise ValueError("Superuser must have is_active = True")

        return self.create_user(email, password, **extra_fields)