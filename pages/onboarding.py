"""
Onboarding Page - Collect initial user information
"""
from datetime import date, timedelta
from decimal import Decimal

import streamlit as st

from config.database import db
from src.middleware import auth_middleware
from src.models import FinancialGoal, FinancialSituation
from src.repositories import FinancialGoalRepository, FinancialSituationRepository
from src.services import InvestmentPreferenceService, UserService
from src.utils.async_helpers import run_async

st.set_page_config(
    page_title="Onboarding - BUJA",
    page_icon="👋",
    layout="wide"
)

# Authentication check
if not auth_middleware.is_authenticated():
    st.warning("Login required.")
    st.switch_page("pages/login.py")
    st.stop()

user = auth_middleware.get_current_user()
user_service = UserService()
preference_service = InvestmentPreferenceService()
financial_situation_repo = FinancialSituationRepository(db)
financial_goal_repo = FinancialGoalRepository(db)

# Render common sidebar
from src.utils.sidebar import render_sidebar

render_sidebar()

st.title("👋 Welcome! Welcome to BUJA")
st.markdown("""
**빠른 시작**: 최소 정보만 입력하면 바로 포트폴리오를 제안해드립니다.
상세 정보는 나중에 언제든지 추가할 수 있습니다.
""")

# Display progress steps
if "onboarding_step" not in st.session_state:
    st.session_state.onboarding_step = 1

# 간소화된 2단계 온보딩
steps = ["1. 기본 정보", "2. 투자 목표"]
current_step = st.session_state.onboarding_step

# Progress bar
progress = current_step / len(steps)
st.progress(progress)
st.caption(f"Step {current_step}/{len(steps)}: {steps[current_step - 1]}")

# Step 1: Basic Information (UserProfile) - 간소화
if current_step == 1:
    st.subheader("📋 기본 정보")

    # Check existing profile information
    try:
        user_with_profile = run_async(user_service.get_user_with_profile(user.id))
        existing_profile = user_with_profile.profile
    except Exception:
        existing_profile = None

    with st.form("profile_form"):
        st.info("💡 이름과 나이만 입력하면 바로 시작할 수 있습니다. 직업은 선택사항입니다.")

        name = st.text_input(
            "이름 *",
            value=existing_profile.name if existing_profile and existing_profile.name else "",
            placeholder="홍길동"
        )

        age = st.number_input(
            "나이 *",
            min_value=1,
            max_value=120,
            value=existing_profile.age if existing_profile and existing_profile.age else None,
            help="나이를 입력해주세요"
        )

        occupation = st.text_input(
            "직업 (선택사항)",
            value=existing_profile.occupation if existing_profile and existing_profile.occupation else "",
            placeholder="예: 개발자, 회계사, 의사 등"
        )

        submit = st.form_submit_button("다음", use_container_width=True)

        if submit:
            if not name or not age:
                st.error("이름과 나이는 필수 입력 항목입니다.")
            else:
                try:
                    # Update profile
                    profile_data = {
                        "name": name,
                        "age": int(age),
                        "occupation": occupation if occupation else None
                    }
                    run_async(user_service.update_profile(user.id, profile_data))
                    st.session_state.onboarding_step = 2
                    st.rerun()
                except Exception as e:
                    st.error(f"프로필 저장 오류: {str(e)}")

# Step 2: Quick Investment Goal - 간소화된 투자 목표 설정
elif current_step == 2:
    st.subheader("💰 투자 목표")

    # Check existing data
    try:
        existing_situation = run_async(financial_situation_repo.get_by_user_id(user.id))
    except Exception:
        existing_situation = None

    try:
        existing_preference = run_async(preference_service.get_preference(user.id))
    except Exception:
        existing_preference = None

    with st.form("quick_investment_form"):
        st.info("💡 최소 정보만 입력하면 바로 포트폴리오를 제안해드립니다. 상세 정보는 나중에 추가할 수 있습니다.")

        col1, col2 = st.columns(2)

        with col1:
            total_assets = st.number_input(
                "시작 자산 (원) *",
                min_value=0,
                value=int(existing_situation.total_assets) if existing_situation and existing_situation.total_assets else 0,
                step=1000000,
                help="현재 투자 가능한 금액 또는 이미 투자한 금액"
            )

            monthly_investment = st.number_input(
                "월 투자 가능액 (원)",
                min_value=0,
                value=int(existing_situation.monthly_income - existing_situation.monthly_expense) if existing_situation and existing_situation.monthly_income and existing_situation.monthly_expense else 0,
                step=100000,
                help="매월 추가로 투자할 수 있는 금액 (선택사항)"
            )

        with col2:
            target_return = st.number_input(
                "목표 수익률 (%) *",
                min_value=0.0,
                max_value=100.0,
                value=float(existing_preference.target_return) if existing_preference and existing_preference.target_return else 10.0,
                step=0.5,
                help="연간 목표 수익률"
            )

            risk_tolerance = st.slider(
                "위험 감수 성향 (1-10) *",
                min_value=1,
                max_value=10,
                value=existing_preference.risk_tolerance if existing_preference else 5,
                help="1=매우 보수적, 10=매우 공격적"
            )

        # 상세 정보 접기/펼치기
        with st.expander("📋 상세 정보 입력 (선택사항)", expanded=False):
            st.caption("더 정확한 추천을 위해 추가 정보를 입력할 수 있습니다. 나중에 언제든지 수정 가능합니다.")

            col1, col2 = st.columns(2)

            with col1:
                detail_monthly_income = st.number_input(
                    "월 소득 (원)",
                    min_value=0,
                    value=int(existing_situation.monthly_income) if existing_situation and existing_situation.monthly_income else 0,
                    step=100000,
                    key="detail_monthly_income"
                )

                detail_monthly_expense = st.number_input(
                    "월 지출 (원)",
                    min_value=0,
                    value=int(existing_situation.monthly_expense) if existing_situation and existing_situation.monthly_expense else 0,
                    step=100000,
                    key="detail_monthly_expense"
                )

            with col2:
                detail_total_debt = st.number_input(
                    "총 부채 (원)",
                    min_value=0,
                    value=int(existing_situation.total_debt) if existing_situation and existing_situation.total_debt else 0,
                    step=1000000,
                    key="detail_total_debt"
                )

                detail_emergency_fund = st.number_input(
                    "비상금 (원)",
                    min_value=0,
                    value=int(existing_situation.emergency_fund) if existing_situation and existing_situation.emergency_fund else 0,
                    step=1000000,
                    key="detail_emergency_fund"
                )

        col_prev, col_complete = st.columns([1, 1])
        with col_prev:
            if st.form_submit_button("이전", use_container_width=True):
                st.session_state.onboarding_step = 1
                st.rerun()

        with col_complete:
            submit = st.form_submit_button("✅ 완료하고 포트폴리오 받기", use_container_width=True)

        if submit:
            if not total_assets or total_assets == 0:
                st.error("시작 자산은 필수 입력 항목입니다.")
            else:
                try:
                    # Save financial situation
                    # expander 안의 변수들은 form submit 시에도 접근 가능
                    monthly_income_val = detail_monthly_income if 'detail_monthly_income' in locals() else 0
                    monthly_expense_val = detail_monthly_expense if 'detail_monthly_expense' in locals() else 0
                    total_debt_val = detail_total_debt if 'detail_total_debt' in locals() else 0
                    emergency_fund_val = detail_emergency_fund if 'detail_emergency_fund' in locals() else 0
                    
                    async def save_data():
                        # Financial Situation 저장
                        if existing_situation:
                            existing_situation.monthly_income = Decimal(str(monthly_income_val)) if monthly_income_val else None
                            existing_situation.monthly_expense = Decimal(str(monthly_expense_val)) if monthly_expense_val else None
                            existing_situation.total_assets = Decimal(str(total_assets))
                            existing_situation.total_debt = Decimal(str(total_debt_val)) if total_debt_val else None
                            existing_situation.emergency_fund = Decimal(str(emergency_fund_val)) if emergency_fund_val else None
                            async with db.session() as session:
                                await financial_situation_repo.update(existing_situation, session)
                                await session.commit()
                        else:
                            situation = FinancialSituation(
                                user_id=user.id,
                                monthly_income=Decimal(str(monthly_income_val)) if monthly_income_val else None,
                                monthly_expense=Decimal(str(monthly_expense_val)) if monthly_expense_val else None,
                                total_assets=Decimal(str(total_assets)),
                                total_debt=Decimal(str(total_debt_val)) if total_debt_val else None,
                                emergency_fund=Decimal(str(emergency_fund_val)) if emergency_fund_val else None,
                                family_members=1,
                                insurance_coverage=None
                            )
                            async with db.session() as session:
                                await financial_situation_repo.create(situation, session)
                                await session.commit()

                        # Investment Preference 저장
                        preference_data = {
                            "risk_tolerance": risk_tolerance,
                            "target_return": target_return,
                            "investment_period": "MEDIUM",  # 기본값
                            "investment_experience": "BEGINNER",  # 기본값
                            "max_loss_tolerance": 20.0,  # 기본값
                            "preferred_asset_types": None,
                            "home_country": "KOREA",  # 기본값
                            "preferred_regions": ["KOREA", "USA"],  # 기본값
                            "currency_hedge_preference": "NONE"  # 기본값
                        }
                        await preference_service.update_preference(user.id, preference_data)

                    run_async(save_data())

                    # 온보딩 완료
                    st.session_state.onboarding_completed = True
                    st.success("🎉 온보딩이 완료되었습니다! Agent Chat으로 이동합니다.")
                    import time
                    time.sleep(1)
                    st.switch_page("pages/agent_chat.py")
                except Exception as e:
                    st.error(f"데이터 저장 오류: {str(e)}")

# Step 3, 4는 제거됨 - 간소화된 온보딩으로 통합
# 기존 Step 3, 4는 나중에 상세 정보 입력 페이지로 활용 가능
if False:  # 사용 안 함
    st.subheader("📈 Investment Preference")

    # Check existing investment preference
    try:
        existing_preference = run_async(preference_service.get_preference(user.id))
    except Exception:
        existing_preference = None

    with st.form("preference_form"):
        risk_tolerance = st.slider(
            "Risk Tolerance (1-10) *",
            min_value=1,
            max_value=10,
            value=existing_preference.risk_tolerance if existing_preference else 5,
            help="1 = Very Conservative, 10 = Very Aggressive"
        )

        st.markdown("**Risk Tolerance Guide:**")
        st.info("""
        - **1-3 (Conservative)**: Capital preservation is top priority, seeking stable returns
        - **4-6 (Moderate)**: Accepting moderate risk while seeking returns
        - **7-10 (Aggressive)**: Accepting high risk for high returns
        """)

        # Auto-calculate target return based on financial goals
        calculated_target_return = None
        try:
            financial_goals = run_async(financial_goal_repo.get_by_user_id(user.id))
            financial_situation = run_async(financial_situation_repo.get_by_user_id(user.id))

            if financial_goals and financial_situation and financial_situation.total_assets:
                # Use highest priority goal
                primary_goal = max(financial_goals, key=lambda g: g.priority, default=None)
                if primary_goal:
                    from datetime import date
                    today = date.today()
                    years = (primary_goal.target_date - today).days / 365.25

                    if years > 0:
                        current_amount = float(financial_situation.total_assets)
                        target_amount = float(primary_goal.target_amount)
                        needed_amount = target_amount - current_amount

                        if needed_amount > 0 and current_amount > 0:
                            # Calculate required return: (target_amount / current_amount)^(1/years) - 1
                            import math
                            required_return = (math.pow(target_amount / current_amount, 1 / years) - 1) * 100
                            calculated_target_return = max(0.0, min(100.0, required_return))
        except Exception:
            pass

        # Target return input (display auto-calculated value if available)
        if calculated_target_return:
            st.info(f"💡 Target return calculated based on financial goals: **{calculated_target_return:.2f}%**")
            st.caption(f"This is the annual average return needed to achieve {primary_goal.target_amount:,.0f} KRW by {primary_goal.target_date.strftime('%B %Y')}.")

        target_return = st.number_input(
            "Target Return (%) *",
            min_value=0.0,
            max_value=100.0,
            value=calculated_target_return if calculated_target_return else (float(existing_preference.target_return) if existing_preference and existing_preference.target_return else 7.0),
            step=0.1,
            help="If you have financial goals, the auto-calculated value will be displayed. You can modify it if needed."
        )

        if calculated_target_return and abs(target_return - calculated_target_return) > 0.1:
            st.warning("⚠️ The entered target return differs from the calculated value. It may be difficult to achieve your financial goals.")

        investment_period = st.selectbox(
            "Investment Period *",
            options=["SHORT", "MEDIUM", "LONG"],
            index=0 if not existing_preference else ["SHORT", "MEDIUM", "LONG"].index(existing_preference.investment_period) if existing_preference.investment_period in ["SHORT", "MEDIUM", "LONG"] else 0,
            help="SHORT: 1 year or less, MEDIUM: 1-5 years, LONG: 5 years or more"
        )

        investment_experience = st.selectbox(
            "Investment Experience *",
            options=["BEGINNER", "INTERMEDIATE", "ADVANCED"],
            index=0 if not existing_preference else ["BEGINNER", "INTERMEDIATE", "ADVANCED"].index(existing_preference.investment_experience) if existing_preference.investment_experience in ["BEGINNER", "INTERMEDIATE", "ADVANCED"] else 0
        )

        max_loss_tolerance = st.number_input(
            "Max Loss Tolerance (%)",
            min_value=0.0,
            max_value=100.0,
            value=float(existing_preference.max_loss_tolerance) if existing_preference and existing_preference.max_loss_tolerance else 20.0,
            step=0.1,
            help="Maximum acceptable loss ratio in portfolio"
        )

        preferred_asset_types = st.multiselect(
            "Preferred Asset Types",
            options=["STOCK", "BOND", "REAL_ESTATE", "CRYPTO", "COMMODITY", "ETF", "MUTUAL_FUND"],
            default=existing_preference.preferred_asset_types if existing_preference and existing_preference.preferred_asset_types else []
        )

        st.markdown("---")
        st.markdown("### 🌍 Global Portfolio Settings")

        with st.expander("💡 What is a Global Portfolio?", expanded=False):
            st.markdown("""
            **Global Portfolio** is a strategy of diversifying investments across multiple countries and regions worldwide.
            
            **Advantages:**
            - Risk diversification by leveraging regional economic cycle differences
            - Access to emerging markets with high growth potential
            - Currency diversification to mitigate exchange rate risk
            
            **Recommended Regions:**
            - **Korea**: Home market, no currency risk
            - **USA**: World's largest market, dollar-based
            - **Europe**: Developed markets, euro/pound diversification
            - **Asia**: Growth potential, yuan/yen diversification
            - **Emerging Markets**: High growth rates, diverse currencies
            """)

        home_country = st.selectbox(
            "Home Country (Base Currency) *",
            options=["KOREA", "USA", "JAPAN", "CHINA", "EUROPE", "SINGAPORE", "OTHER"],
            index=0 if not existing_preference or not existing_preference.home_country else
                  ["KOREA", "USA", "JAPAN", "CHINA", "EUROPE", "SINGAPORE", "OTHER"].index(existing_preference.home_country)
                  if existing_preference.home_country in ["KOREA", "USA", "JAPAN", "CHINA", "EUROPE", "SINGAPORE", "OTHER"] else 0,
            help="Selecting your home country will configure the portfolio based on that country's currency."
        )

        preferred_regions = st.multiselect(
            "Preferred Investment Regions (Multiple Selection)",
            options=["KOREA", "USA", "EUROPE", "ASIA", "EMERGING", "GLOBAL"],
            default=existing_preference.preferred_regions if existing_preference and existing_preference.preferred_regions else ["KOREA", "USA"],
            help="Select regions you want to invest in. Selecting multiple regions will diversify your assets."
        )

        currency_hedge_preference = st.selectbox(
            "Currency Hedge Preference",
            options=["NONE", "PARTIAL", "FULL"],
            index=0 if not existing_preference or not existing_preference.currency_hedge_preference else
                  ["NONE", "PARTIAL", "FULL"].index(existing_preference.currency_hedge_preference)
                  if existing_preference.currency_hedge_preference in ["NONE", "PARTIAL", "FULL"] else 0,
            help="Select the degree of hedging for exchange rate risk. NONE=No hedge, PARTIAL=Partial hedge, FULL=Full hedge"
        )

        with st.expander("💡 What is Currency Hedging?", expanded=False):
            st.markdown("""
            **Currency Hedging** is a strategy to prevent losses from exchange rate fluctuations when investing in foreign currency assets.
            
            **NONE (No Hedge):**
            - Accept exchange rate fluctuation risk as is
            - Potential for additional returns when exchange rate rises, potential losses when it falls
            - No cost
            
            **PARTIAL (Partial Hedge):**
            - Hedge only part of the portfolio (usually 50-70%)
            - Balance between exchange rate risk and profit opportunities
            - Moderate cost
            
            **FULL (Full Hedge):**
            - Hedge most of the portfolio
            - Minimize exchange rate fluctuation risk
            - Hedging costs incurred
            """)

        col_prev, col_next = st.columns([1, 1])
        with col_prev:
            if st.form_submit_button("Previous", use_container_width=True):
                st.session_state.onboarding_step = 2
                st.rerun()

        with col_next:
            submit = st.form_submit_button("Next", use_container_width=True)

        if submit:
            try:
                preference_data = {
                    "risk_tolerance": risk_tolerance,
                    "target_return": target_return,
                    "investment_period": investment_period,
                    "investment_experience": investment_experience,
                    "max_loss_tolerance": max_loss_tolerance,
                    "preferred_asset_types": preferred_asset_types if preferred_asset_types else None,
                    "home_country": home_country,
                    "preferred_regions": preferred_regions if preferred_regions else None,
                    "currency_hedge_preference": currency_hedge_preference
                }

                run_async(preference_service.update_preference(user.id, preference_data))
                st.session_state.onboarding_step = 4
                st.rerun()
            except Exception as e:
                st.error(f"Error saving investment preference: {str(e)}")

# Step 4: Financial Goals
elif current_step == 4:
    st.subheader("🎯 Financial Goals")

    # Financial goals explanation
    with st.expander("💡 What are Financial Goals?", expanded=False):
        st.markdown("""
        **Financial Goals** are financial objectives you want to achieve in the future.
        
        For example:
        - 🏠 **House Purchase**: Goal to transition from rental to homeownership
        - 🎓 **Education Fund**: Savings goal for children's college tuition
        - 🏖️ **Travel/Vacation**: Goal for a dream overseas trip
        - 🏦 **Emergency Fund**: Emergency funds for unexpected situations
        - 👴 **Retirement Planning**: Long-term savings goal for retirement
        - 💼 **Other**: Personal goals such as starting a business, business expansion, etc.
        
        You can add multiple goals and set **priority** for each goal to use in investment strategy planning.
        """)

    st.info("💡 Add your financial goals. You can add multiple goals, and investment plans will be created based on priority.")

    # Check existing goals
    try:
        existing_goals = run_async(financial_goal_repo.get_by_user_id(user.id))
    except Exception:
        existing_goals = []

    if existing_goals:
        st.subheader("📋 Currently Registered Goals")
        for goal in existing_goals:
            # Convert goal type to display name
            goal_type_display_map = {
                "RETIREMENT": "Retirement Planning",
                "HOUSE": "House Purchase",
                "EDUCATION": "Education Fund",
                "TRAVEL": "Travel/Vacation",
                "EMERGENCY": "Emergency Fund",
                "OTHER": "Other"
            }
            goal_type_display = goal_type_display_map.get(goal.goal_type, goal.goal_type)

            with st.expander(f"🎯 {goal_type_display} - {goal.target_amount:,.0f} KRW (Target Date: {goal.target_date.strftime('%B %d, %Y')})"):
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Priority", f"#{goal.priority}", help="Priority #1 is the highest priority")
                with col2:
                    progress_pct = (goal.current_progress / goal.target_amount * 100) if goal.target_amount > 0 else 0
                    st.metric("Progress", f"{progress_pct:.1f}%", f"{goal.current_progress:,.0f} KRW / {goal.target_amount:,.0f} KRW")

                if st.button("🗑️ Delete", key=f"delete_{goal.id}", use_container_width=True):
                    async def delete_goal():
                        async with db.session() as session:
                            await financial_goal_repo.delete(goal.id, session)
                            await session.commit()
                    run_async(delete_goal())
                    st.rerun()

    with st.form("goal_form"):
        st.markdown("### Add New Goal")

        # Display goal type options
        goal_type_options = {
            "Retirement Planning": "RETIREMENT",
            "House Purchase": "HOUSE",
            "Education Fund": "EDUCATION",
            "Travel/Vacation": "TRAVEL",
            "Emergency Fund": "EMERGENCY",
            "Other": "OTHER"
        }

        goal_type_display = st.selectbox(
            "Goal Type *",
            options=list(goal_type_options.keys()),
            help="Select the type of financial goal you want to achieve"
        )
        goal_type = goal_type_options[goal_type_display]

        col1, col2 = st.columns(2)

        with col1:
            target_amount = st.number_input(
                "Target Amount (KRW) *",
                min_value=0,
                step=1000000,
                format="%d",
                help="Enter the target amount you want to achieve"
            )

        with col2:
            # Can set up to 50 years from current date
            max_date = date.today() + timedelta(days=365 * 50)
            target_date = st.date_input(
                "Target Date *",
                min_value=date.today() + timedelta(days=1),
                max_value=max_date,
                value=date.today() + timedelta(days=365),
                help=f"Select the date you want to achieve the goal (up to {max_date.year})"
            )

        st.markdown("---")

        # Priority explanation
        with st.expander("💡 What is Priority?", expanded=False):
            st.markdown("""
            **Priority** is a criterion for determining which goal to achieve first among multiple financial goals.
            
            - **Priority 1 (Highest)**: Most important and urgent goals (e.g., emergency fund, short-term goals)
            - **Priority 2-3**: Important but less time-sensitive goals (e.g., house purchase, education fund)
            - **Priority 4-5**: Long-term and less urgent goals (e.g., retirement planning, travel)
            
            Investment strategy and fund allocation vary based on priority.
            """)

        priority = st.slider(
            "Priority",
            min_value=1,
            max_value=5,
            value=3,
            help="1 = Highest (most important), 5 = Low priority",
            format="#%d"
        )

        # Display priority description
        priority_descriptions = {
            1: "🔥 Highest - Most important and urgent goal",
            2: "⭐ High - Important goal",
            3: "📌 Medium - General goal",
            4: "📋 Low - Less urgent goal",
            5: "💤 Very Low - Long-term goal"
        }
        st.caption(f"💡 {priority_descriptions[priority]}")

        st.markdown("---")

        col_prev, col_add, col_next = st.columns([1, 1, 1])
        with col_prev:
            if st.form_submit_button("⬅️ Previous", use_container_width=True):
                st.session_state.onboarding_step = 3
                st.rerun()

        with col_add:
            add_goal = st.form_submit_button("➕ Add Goal", use_container_width=True)

        with col_next:
            finish = st.form_submit_button("✅ Complete", use_container_width=True)

        if add_goal:
            if not target_amount:
                st.error("❌ Please enter the target amount.")
            elif target_date <= date.today():
                st.error("❌ Target date must be after today.")
            else:
                try:
                    goal = FinancialGoal(
                        user_id=user.id,
                        goal_type=goal_type,
                        target_amount=Decimal(str(target_amount)),
                        target_date=target_date,
                        priority=priority,
                        current_progress=Decimal("0")
                    )
                    async def create_goal():
                        async with db.session() as session:
                            await financial_goal_repo.create(goal, session)
                            await session.commit()
                    run_async(create_goal())
                    st.success(f"✅ Goal has been added! ({goal_type_display})")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error adding goal: {str(e)}")

        if finish:
            # Can complete even if no goals (optional)
            if not existing_goals:
                st.info("💡 Financial goals are optional. You can add them anytime later.")

            # Set onboarding completion flag
            st.session_state.onboarding_completed = True
            st.success("🎉 Onboarding completed! Redirecting to Agent Chat.")
            import time
            time.sleep(1)
            st.switch_page("pages/agent_chat.py")

