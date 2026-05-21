import random
from app.database.database import engine
from app.database.models import PredictionLog
from sqlalchemy.orm import Session

def seed_data():
    with Session(engine) as session:
        for _ in range(100):
            churn_prob = random.random()
            pred = 1 if churn_prob > 0.5 else 0
            
            log = PredictionLog(
                gender=random.choice(["Male", "Female"]),
                tenure=random.randint(1, 72),
                monthly_charges=random.uniform(20, 120),
                total_charges=random.uniform(20, 8000),
                prediction=pred,
                churn_probability=churn_prob
            )
            session.add(log)
        session.commit()
    print("Seeded 100 predictions")

if __name__ == "__main__":
    seed_data()
