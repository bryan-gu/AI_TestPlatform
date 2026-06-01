from pydantic import BaseModel


class DashboardStats(BaseModel):
    activeProjects: int = 0
    totalCases: int = 0
    newCases: int = 0
    passRate: int = 0
    passRateChange: float = 0.0
    pendingBugs: int = 0
    severeBugs: int = 0
    normalBugs: int = 0


class ActivityOut(BaseModel):
    icon: str
    text: str
    time: str = ""
    user: str = ""
