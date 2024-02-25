import re


class CardCheck:
    @staticmethod
    def validate_luhn(card_number: str) -> bool:
        card_number = str(card_number)
        if not card_number.isdigit():
            return False
        total_sum = 0
        is_second_digit = False
        for digit in reversed(card_number):
            digit = int(digit)
            if is_second_digit:
                digit *= 2
                if digit > 9:
                    digit -= 9
            total_sum += digit
            is_second_digit = not is_second_digit
        return total_sum % 10 == 0

    @staticmethod
    async def preprocess_phone(phone: str) -> str:
        formatted_number = re.sub(r'[+\s\-()]', '', phone)
        if formatted_number.startswith('8') or formatted_number.startswith('7'):
            formatted_number = '+7' + formatted_number[1:]
        return formatted_number
