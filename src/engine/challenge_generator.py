import random

CHALLENGE_POOL = {
    'eye': ['blink_once', 'blink_twice'],
    'head': ['look_left', 'look_right', 'look_up', 'look_down'],
    'hands': ['raise_open_palm', 'thumbs_up'],
    'face': ['smile']
}

class ChallengeGenerator:
    """Generates a random sequence of 3 challenges for liveness verification."""
    
    @staticmethod
    def generate_challenges(count: int = 3) -> list:
        """
        Selects exactly `count` unique challenges.
        Ensures variety by attempting to pick from different categories.
        """
        categories = list(CHALLENGE_POOL.keys())
        selected_challenges = []
        
        # Pick categories ensuring variety
        sampled_categories = random.sample(categories, min(count, len(categories)))
        if count > len(categories):
            # If we need more tasks than categories, sample with replacement for the rest
            sampled_categories += random.choices(categories, k=count - len(categories))
            
        random.shuffle(sampled_categories)
        
        for cat in sampled_categories:
            task = random.choice(CHALLENGE_POOL[cat])
            # Avoid duplicate tasks
            while task in selected_challenges:
                task = random.choice(CHALLENGE_POOL[cat])
            selected_challenges.append(task)
            
        return selected_challenges
