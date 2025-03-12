import datetime
import json
import random
import string
from typing import List

from app.core.config import settings
from app.entity.invitation_code import InvitationCode


class InvitationCodeUtils:

    def __init__(self, file_path: str = "static/invitation_code.json"):
        self.file_path = file_path

    def _get_invitation_codes(self) -> List[InvitationCode]:
        """
        Get all the invitation codes from the file
        """
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                content = f.read()
                if not content.strip():
                    return []
                data = json.loads(content)
                return [InvitationCode.from_dict(d) for d in data.get("invitation_codes", [])]
        except FileNotFoundError:
            return []

    def _save_invitation_codes(self, invitation_codes: List[InvitationCode]):
        """
        Save the invitation codes to the file
        """
        with open(self.file_path, "w", encoding="utf-8") as f:
            content = json.dumps({"invitation_codes": [code.to_dict() for code in invitation_codes]}, indent=4)
            f.write(content)

    def generate_invitation_code(self) -> InvitationCode:
        """
        Generate a new invitation code and save it to the file
        """
        existing_invitation_codes = self._get_invitation_codes()  # Get all the existing invitation codes

        code_str = ''.join(random.choices(string.ascii_letters + string.digits, k=8))  # Generate a random code
        while any([code.code == code_str for code in existing_invitation_codes]):  # Check if the code is already used
            code_str = ''.join(random.choices(string.ascii_letters + string.digits, k=8))  # Generate a new random code
        expiration_time = datetime.datetime.now() + datetime.timedelta(
            days=settings.INVITATION_CODE_EXPIRE_TIME)  # Calculate the expiration time
        invitation_code = InvitationCode(code=code_str, expiration_time=expiration_time,
                                         used=False)  # Create a new invitation code object

        existing_invitation_codes.append(invitation_code)  # Add the new invitation code to the list

        self._save_invitation_codes(existing_invitation_codes)  # Save the new list to the file
        return invitation_code

    def check_invitation_code(self, invitation_code: str) -> bool:
        """
        Check if the invitation code is valid
        """
        result = False
        existing_invitation_codes = self._get_invitation_codes()  # Get all the existing invitation codes
        # check if the invitation code is in the list and is active
        for code in existing_invitation_codes:
            if code.code == invitation_code and code.is_active:
                code.used = True
                result = True
                break
        # Save the new list to the file
        self._save_invitation_codes(existing_invitation_codes)
        # Return the result
        return result
