/* ------------------------------------------------------------------ */
/* Avatar dropdown                                                     */
/* ------------------------------------------------------------------ */
(function () {
    const btn      = document.getElementById('avatar-btn');
    const dropdown = document.getElementById('avatar-dropdown');
    if (!btn) return;

    btn.addEventListener('click', function (e) {
        e.stopPropagation();
        dropdown.classList.toggle('open');
    });

    dropdown.addEventListener('click', function (e) {
        e.stopPropagation();
    });

    document.addEventListener('click', function () {
        dropdown.classList.remove('open');
    });

    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') dropdown.classList.remove('open');
    });
})();

/* ------------------------------------------------------------------ */
/* Dark mode                                                           */
/* ------------------------------------------------------------------ */
(function () {
    const toggle   = document.getElementById('dark-mode-toggle');
    const themeIcon = document.getElementById('theme-icon');
    const root     = document.documentElement;

    function applyTheme(dark) {
        root.setAttribute('data-theme', dark ? 'dark' : 'light');
        if (toggle)    toggle.checked = dark;
        if (themeIcon) themeIcon.textContent = dark ? '☀️' : '🌙';
    }

    applyTheme(localStorage.getItem('theme') === 'dark');

    if (toggle) {
        toggle.addEventListener('change', function () {
            const dark = this.checked;
            localStorage.setItem('theme', dark ? 'dark' : 'light');
            applyTheme(dark);
        });
    }
})();

/* ------------------------------------------------------------------ */
/* Tips                                                                */
/* ------------------------------------------------------------------ */

const TIPS = [
  "Track every ₹10 — small leaks sink big ships.",
  "Set a monthly budget before the month begins, not after.",
  "Pay yourself first: save before you spend.",
  "The best time to start saving was yesterday. Second best: today.",
  "Avoid buying on impulse — wait 24 hours before any unplanned purchase.",
  "Cook at home twice more per week and watch your food bill shrink.",
  "Cancel subscriptions you haven't used in 30 days.",
  "Round up every expense to the nearest ₹50 in your head — you'll spend less.",
  "A ₹50/day coffee habit costs ₹18,250 a year.",
  "Emergency fund first — aim for 3 months of expenses.",
  "Automate your savings so you never have to think about it.",
  "Review your bank statement every Sunday — surprises cost money.",
  "Buy in bulk only when you'll actually use it before it expires.",
  "Switch to a prepaid phone plan and cut your bill in half.",
  "Use cash for groceries — physical money feels more real.",
  "Meal prep on Sundays to avoid expensive weekday takeouts.",
  "Never shop hungry — you'll spend 30% more.",
  "The free trial you forgot to cancel is costing you right now.",
  "Negotiate your rent before signing — landlords expect it.",
  "A budget isn't a restriction, it's a plan for your money.",
  "Split large expenses across months using zero-interest EMIs wisely.",
  "Compare prices across 3 places before any purchase above ₹500.",
  "Unsubscribe from promotional emails — out of sight, out of cart.",
  "Walk or cycle for short trips and save on fuel and health.",
  "The cheapest product isn't always the best value.",
  "Track net worth, not just income — assets minus liabilities.",
  "Spending ₹100 less today is the same as earning ₹100 more.",
  "Buy second-hand for items you'll use less than once a week.",
  "Turn off lights, fans, and AC when leaving a room — it adds up.",
  "Your future self will thank you for every rupee you save today.",
  "Avoid ATM fees — plan your cash withdrawals in advance.",
  "A ₹500/month investment at 12% grows to ₹50 lakh in 30 years.",
  "Don't confuse lifestyle inflation with quality of life.",
  "Shop with a list — lists prevent impulse buys.",
  "Review your insurance policies annually — you may be over-covered.",
  "Drink water instead of cold drinks when eating out — saves ₹100+ per meal.",
  "The best investment is in skills that increase your income.",
  "Avoid store credit cards — their interest rates are brutal.",
  "Check for student, senior, or member discounts before every purchase.",
  "Renting is not always worse than buying — do the maths.",
  "One 'no spend' day per week adds up to 52 free days a year.",
  "Give every rupee a job — zero-based budgeting works.",
  "Separate wants from needs before opening your wallet.",
  "A library card gives you thousands of books for free.",
  "Keep a 'wish list' and revisit it after 7 days before buying.",
  "Credit card rewards only make sense if you pay in full every month.",
  "Energy-efficient appliances pay for themselves within 2 years.",
  "DIY before you hire — YouTube can teach you most basic repairs.",
  "Compare electricity and internet plans every year.",
  "Batch your errands to save fuel and time.",
  "Side income, however small, accelerates every financial goal.",
  "Avoid the 'just this once' trap — it's never just once.",
  "The ₹200 you spend on lottery tickets is a guaranteed loss.",
  "Invest in index funds over single stocks for lower risk.",
  "Keep fixed costs (rent, EMIs) under 50% of your income.",
  "A spending journal reveals patterns you'd never notice otherwise.",
  "Social pressure is the most expensive thing you'll ever give in to.",
  "Experiences over things — memories outlast gadgets.",
  "Review your SIPs once a year, not every market dip.",
  "Buy seasonal produce — it's cheaper and fresher.",
  "Carry a reusable water bottle and stop buying packaged water.",
  "The best sale is the one you don't shop at.",
  "High-interest debt is a fire — put it out before investing.",
  "Pack lunch three days a week and save ₹3,000+ per month.",
  "Turn hobbies into side income — it doubles the value.",
  "Avoid 'buy one get one' deals on things you don't need.",
  "A ₹1,000 monthly SIP started at 25 beats ₹5,000 started at 35.",
  "Know your break-even point on every EMI purchase.",
  "Spend on health now or spend far more on hospitals later.",
  "Financial stress costs more than money — it costs sleep and health.",
  "Keeping up with the Joneses will bankrupt you. The Joneses are broke.",
  "Use UPI cashback offers — free money for spending you'd do anyway.",
  "Review subscriptions every quarter — streaming platforms multiply silently.",
  "A weekend trip planned a month ahead costs half a last-minute one.",
  "Clothes on sale aren't cheap if you didn't need them.",
  "Know your hourly rate — is this purchase worth X hours of your life?",
  "Term life insurance is far cheaper than endowment plans.",
  "Park your emergency fund in a liquid mutual fund, not a savings account.",
  "Fuel up in the morning — petrol is denser in the cool.",
  "Childproofing finances: set up a nominee on every account.",
  "Never invest in something you can't explain in one sentence.",
  "Your credit score affects your loan interest — check it free annually.",
  "Consolidate small debts into one to simplify and reduce interest.",
  "Office pantry coffee over café coffee saves ₹2,000+ a month.",
  "Eating out is a reward, not a default.",
  "Refill your water purifier filter on time — neglect costs more.",
  "Annual fees on cards are only worth it if you use the benefits.",
  "A joint account for household expenses keeps things transparent.",
  "Don't let tax-saving be your only reason to invest.",
  "Review your mutual fund expense ratio — lower is better.",
  "Financial independence is freedom — start earlier than feels necessary.",
  "Small consistent habits beat large sporadic efforts every time.",
  "Money saved in your 20s is worth 4x money saved in your 40s.",
  "Avoid lending money you can't afford to lose.",
  "The best budget app is the one you'll actually use.",
  "Tracking expenses is not about guilt — it's about awareness.",
  "You don't need more income. You need to know where it goes.",
  "Financial clarity is the first step to financial freedom.",
];

(function () {
  const tipBody = document.querySelector(".tip-body");
  const tipCard = document.querySelector(".mock-float-tip");
  const tipBtn  = document.querySelector(".tip-btn");

  if (tipBody) {
    tipBody.textContent = TIPS[Math.floor(Math.random() * TIPS.length)];
  }

  if (tipBtn && tipCard) {
    tipBtn.addEventListener("click", function () {
      tipCard.classList.add("dismissed");
      tipCard.addEventListener("transitionend", function () {
        tipCard.style.display = "none";
      }, { once: true });
    });
  }
  const moneyPile = document.querySelector(".money-pile");
  if (moneyPile) {
    moneyPile.addEventListener("click", function () {
      const rect = moneyPile.getBoundingClientRect();
      const cx = rect.left + rect.width  / 2;
      const cy = rect.top  + rect.height / 2;
      const count = 14;

      for (let i = 0; i < count; i++) {
        const angle    = (360 / count) * i + (Math.random() * 18 - 9);
        const distance = 70 + Math.random() * 55;
        const rad      = (angle * Math.PI) / 180;
        const tx       = Math.cos(rad) * distance;
        const ty       = Math.sin(rad) * distance;

        const particle = document.createElement("span");
        particle.className   = "money-particle";
        particle.textContent = "💵";
        particle.style.left  = cx + "px";
        particle.style.top   = cy + "px";
        particle.style.setProperty("--tx", tx + "px");
        particle.style.setProperty("--ty", ty + "px");
        particle.style.animationDelay = (Math.random() * 60) + "ms";
        document.body.appendChild(particle);
        particle.addEventListener("animationend", () => particle.remove(), { once: true });
      }
    });
  }
})();
