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
