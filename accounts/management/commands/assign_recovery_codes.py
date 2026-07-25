from django.core.management.base import BaseCommand
from django.db.models import Q
from accounts.models import Profile
from utils.recovery_service import generate_recovery_code, hash_recovery_code

class Command(BaseCommand):
    help = 'Assigns secure recovery codes to all existing accounts that do not have one.'

    def handle(self, *args, **options):
        # Find profiles with missing or empty recovery code hashes
        profiles = Profile.objects.filter(Q(recovery_code_hash__isnull=True) | Q(recovery_code_hash=''))
        
        count = profiles.count()
        if count == 0:
            self.stdout.write(self.style.SUCCESS('All accounts already have recovery codes assigned.'))
            return

        self.stdout.write(self.style.WARNING(f'Found {count} profile(s) without recovery codes.'))
        self.stdout.write(self.style.WARNING('Generating and assigning codes...\n'))
        
        self.stdout.write(f"{'Username':<20} | {'Email':<30} | {'Recovery Code':<20}")
        self.stdout.write("-" * 80)

        for profile in profiles:
            user = profile.user
            plain_code = generate_recovery_code()
            
            # Hash and save
            profile.recovery_code_hash = hash_recovery_code(plain_code)
            profile.save()
            
            username = user.username if user else "Unknown"
            email = user.email if user else "No Email"
            
            self.stdout.write(f"{username:<20} | {email:<30} | {plain_code:<20}")

        self.stdout.write("\n" + self.style.SUCCESS(f'Successfully assigned recovery codes to {count} profile(s).'))
        self.stdout.write(self.style.SUCCESS('IMPORTANT: Store the printed plain codes securely; they will not be shown again.'))
