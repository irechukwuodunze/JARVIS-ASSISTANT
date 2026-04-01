import os
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends
import google.generativeai as genai
from api.models import (
    ExpenseModel, ExpenseCreateRequest, OpportunityCostResponse,
    FinanceSummaryResponse, UserModel
)
from api.database import (
    get_user_by_id, update_user, create_expense, get_user_expenses,
    get_expenses_by_date_range
)
from api.deps import get_current_user

router = APIRouter()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
genai.configure(api_key=GEMINI_API_KEY)


@router.post("/log-expense")
async def log_expense(expense: ExpenseCreateRequest, current_user = Depends(get_current_user)):
    """Log an expense with AI categorization and CFO analysis"""
    user = await get_user_by_id(str(current_user.id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        # Use Gemini to analyze expense and generate CFO warning
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        persona_context = ""
        if user.persona:
            persona_context = f"""User Profile:
- Monthly Budget: £{user.persona.monthly_budget}
- Hourly Rate: £{user.persona.hourly_rate}
- Daily Goals: {', '.join(user.persona.daily_goals)}
- Procrastination Task: {user.persona.procrastination_task}
"""
        
        # Get current month spending
        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_expenses = await get_expenses_by_date_range(str(current_user.id), month_start, now)
        total_month_spent = sum(e.amount for e in month_expenses)
        
        prompt = f"""You are a Savage CFO PA. Analyze this expense and provide a brutal, honest assessment.

{persona_context}

Expense Details:
- Amount: £{expense.amount}
- Category: {expense.category}
- Description: {expense.description}
- Monthly Budget: £{user.persona.monthly_budget if user.persona else 'Not set'}
- Already Spent This Month: £{total_month_spent}

Respond in JSON format:
{{
    "ai_categorization": "refined category",
    "opportunity_cost_hours": hours_of_work_equivalent,
    "is_flagged": true/false,
    "ai_warning": "Savage CFO message - be blunt, use specific numbers, reference their goals"
}}

If flagged, the warning should:
1. Calculate what the money could have been (hours worked, materials, etc.)
2. Reference their specific goals or budget constraints
3. Be direct and slightly sarcastic (Savage PA tone)
4. Provide actionable advice

Example: "That's £15 for lunch. That's 1.5 hours of work. You've already spent 40% of your monthly budget. At this rate, you won't afford your architecture materials by week 3."
"""
        
        response = model.generate_content(prompt)
        
        import json
        try:
            analysis = json.loads(response.text)
        except:
            analysis = {
                "ai_categorization": str(expense.category),
                "opportunity_cost_hours": expense.amount / (user.persona.hourly_rate or 15),
                "is_flagged": False,
                "ai_warning": None
            }
        
        # Create expense record
        expense_dict = {
            "user_id": str(current_user.id),
            "amount": expense.amount,
            "category": str(expense.category),
            "description": expense.description,
            "ai_categorization": analysis.get("ai_categorization"),
            "opportunity_cost_hours": analysis.get("opportunity_cost_hours", 0),
            "is_flagged": analysis.get("is_flagged", False),
            "ai_warning": analysis.get("ai_warning"),
            "created_at": datetime.utcnow(),
        }
        
        expense_id = await create_expense(expense_dict)
        
        return {
            "id": expense_id,
            "success": True,
            "analysis": analysis,
            "message": analysis.get("ai_warning") if analysis.get("is_flagged") else "Expense logged"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Expense logging error: {str(e)}")


@router.get("/summary")
async def get_finance_summary(current_user = Depends(get_current_user)):
    """Get financial summary with burn rate and budget status"""
    user = await get_user_by_id(str(current_user.id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Get current month expenses
        month_expenses = await get_expenses_by_date_range(str(current_user.id), month_start, now)
        total_spent = sum(e.amount for e in month_expenses)
        flagged_expenses = [e for e in month_expenses if e.is_flagged]
        
        # Calculate burn rate
        days_elapsed = (now - month_start).days + 1
        burn_rate = total_spent / days_elapsed if days_elapsed > 0 else 0
        
        # Calculate days until budget exhausted
        monthly_budget = user.persona.monthly_budget if user.persona else 0
        remaining_budget = monthly_budget - total_spent
        days_until_exhausted = remaining_budget / burn_rate if burn_rate > 0 else float('inf')
        
        percentage_used = (total_spent / monthly_budget * 100) if monthly_budget > 0 else 0
        
        return FinanceSummaryResponse(
            total_spent=total_spent,
            monthly_budget=monthly_budget,
            percentage_used=percentage_used,
            burn_rate=burn_rate,
            days_until_budget_exhausted=days_until_exhausted,
            flagged_expenses=flagged_expenses
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summary error: {str(e)}")


@router.get("/opportunity-cost/{expense_id}")
async def get_opportunity_cost(expense_id: str, current_user = Depends(get_current_user)):
    """Get opportunity cost analysis for an expense"""
    user = await get_user_by_id(str(current_user.id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        # For now, return example
        
        hourly_rate = user.persona.hourly_rate if user.persona else 15
        monthly_budget = user.persona.monthly_budget if user.persona else 500
        
        # Example expense
        expense_amount = 15.0
        hours_of_work = expense_amount / hourly_rate
        percentage_of_budget = (expense_amount / monthly_budget * 100) if monthly_budget > 0 else 0
        
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"""Generate a Savage CFO message about this expense:
- Amount: £{expense_amount}
- Hours of work: {hours_of_work:.1f}
- Percentage of monthly budget: {percentage_of_budget:.1f}%

Be blunt and use specific numbers. Reference what this money could have been used for (materials, project time, etc.)."""
        
        response = model.generate_content(prompt)
        
        return OpportunityCostResponse(
            expense_amount=expense_amount,
            hours_of_work=hours_of_work,
            percentage_of_budget=percentage_of_budget,
            warning_message=response.text
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Opportunity cost error: {str(e)}")
