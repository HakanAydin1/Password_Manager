import string
import secrets

class PasswordGenerator:
    @staticmethod
    def generate_password(length: int = 16, 
                          use_upper: bool = True, 
                          use_digits: bool = True, 
                          use_symbols: bool = True) -> str:
        """
        Generates a secure random password based on customizable parameters.
        Ensures that at least one character from each selected pool is included.
        """
        if length < 4:
            length = 4  # Enforce minimum length for security/safety

        pools = [string.ascii_lowercase]
        if use_upper:
            pools.append(string.ascii_uppercase)
        if use_digits:
            pools.append(string.digits)
        if use_symbols:
            pools.append(string.punctuation)
            
        all_chars = "".join(pools)
        
        # Ensure at least one character from each selected pool is chosen
        password_chars = []
        for pool in pools:
            password_chars.append(secrets.choice(pool))
            
        # Fill the rest with random choices from the combined pools
        while len(password_chars) < length:
            password_chars.append(secrets.choice(all_chars))
            
        # Shuffle the result so the guaranteed characters aren't always at the beginning
        secrets.SystemRandom().shuffle(password_chars)
        
        return "".join(password_chars)
