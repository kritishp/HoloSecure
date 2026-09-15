import os
import datetime
import numpy as np
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, LargeBinary
from sqlalchemy.orm import declarative_base, sessionmaker
from src.utils.logger import setup_logger

Base = declarative_base()
logger = setup_logger("Database")

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    roll_number = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    department = Column(String, nullable=False)
    semester = Column(String, nullable=False)
    section = Column(String, nullable=False)
    embedding = Column(LargeBinary, nullable=False) # Store 512-d float32 array as bytes
    registration_date = Column(DateTime, default=datetime.datetime.utcnow)

class AttendanceLog(Base):
    __tablename__ = 'attendance'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    roll_number = Column(String, nullable=False)
    date = Column(String, nullable=False) # YYYY-MM-DD
    time = Column(String, nullable=False) # HH:MM:SS
    status = Column(String, nullable=False)

class DatabaseManager:
    def __init__(self, db_path: str = "database/attendance.db"):
        db_dir = os.path.dirname(db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
            
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        logger.info(f"Database initialized at {db_path}")

    def register_user(self, roll_number, name, department, semester, section, embedding: np.ndarray):
        """Registers a new user with their face embedding."""
        try:
            existing_user = self.session.query(User).filter_by(roll_number=roll_number).first()
            if existing_user:
                logger.warning(f"User with roll number {roll_number} already exists.")
                return False, "User already exists"
                
            new_user = User(
                roll_number=roll_number,
                name=name,
                department=department,
                semester=semester,
                section=section,
                embedding=embedding.tobytes()
            )
            self.session.add(new_user)
            self.session.commit()
            logger.info(f"User {name} registered successfully.")
            return True, "Success"
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error registering user: {e}")
            return False, str(e)

    def get_all_users(self):
        """Returns all registered users and their embeddings."""
        users = self.session.query(User).all()
        result = []
        for u in users:
            emb = np.frombuffer(u.embedding, dtype=np.float32)
            result.append({
                'roll_number': u.roll_number,
                'name': u.name,
                'embedding': emb
            })
        return result

    def log_attendance(self, roll_number: str, status: str = "Present"):
        """Logs attendance for a user. Prevents duplicate logs on the same day."""
        try:
            now = datetime.datetime.now()
            date_str = now.strftime("%Y-%m-%d")
            time_str = now.strftime("%H:%M:%S")
            
            # Check if already marked present today
            existing_log = self.session.query(AttendanceLog).filter_by(
                roll_number=roll_number, 
                date=date_str
            ).first()
            
            if existing_log:
                logger.info(f"Attendance already marked for {roll_number} today.")
                return False, "Already marked present today"
                
            log = AttendanceLog(
                roll_number=roll_number,
                date=date_str,
                time=time_str,
                status=status
            )
            self.session.add(log)
            self.session.commit()
            logger.info(f"Attendance marked for {roll_number}.")
            return True, "Attendance marked successfully"
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error logging attendance: {e}")
            return False, str(e)

    def export_to_csv_string(self):
        """Generates a CSV string of all attendance logs with full student details."""
        import csv
        import io
        try:
            # Join attendance and users tables
            query = self.session.query(
                AttendanceLog.roll_number,
                User.name,
                User.department,
                User.semester,
                User.section,
                AttendanceLog.date,
                AttendanceLog.time,
                AttendanceLog.status
            ).join(User, AttendanceLog.roll_number == User.roll_number).order_by(AttendanceLog.date.desc(), AttendanceLog.time.desc()).all()
            
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['Roll Number', 'Name', 'Department', 'Semester', 'Section', 'Date', 'Time', 'Status'])
            
            for row in query:
                writer.writerow(row)
                
            return True, output.getvalue()
        except Exception as e:
            logger.error(f"Error exporting to CSV string: {e}")
            return False, str(e)

    def get_stats(self):
        """Returns the total number of registered users and the number of verifications today."""
        try:
            today_str = datetime.datetime.now().strftime("%Y-%m-%d")
            
            total_enrolled = self.session.query(User).count()
            verified_today = self.session.query(AttendanceLog).filter(AttendanceLog.date == today_str).count()
            
            return {
                "total_enrolled": total_enrolled,
                "verified_today": verified_today
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"total_enrolled": 0, "verified_today": 0}
