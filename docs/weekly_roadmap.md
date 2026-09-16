# 🗓️ Week 1 Roadmap (Sep 16 - Sep 22)

> **Time commitment**: 30-45 mins focused coding + commute learning
> **Goal**: Understand HoloSecure fully + start building your own skills

---

## ✅ Today — Tuesday, Sep 16

### Theme: **Own Your Project**

**Coding (30 min):**
1. Open [`challenge_evaluator.py`](file:///Users/kritishpoptani/VT_PROJECT/src/engine/challenge_evaluator.py)
2. Read the blink detection code (lines 67-98) carefully
3. On paper/notes, draw how EAR (Eye Aspect Ratio) works — the 6 eye points, the formula
4. Answer to yourself: *"Why do we use EMA instead of a fixed threshold?"*
5. Close the file. Try writing the blink counter logic from memory (even pseudocode is fine)

**Commute:**
- Watch: [Fireship — "100 seconds of FastAPI"](https://youtube.com) (search this)
- Read the HoloSecure architecture guide you downloaded today

---

## 📅 Wednesday, Sep 17

### Theme: **Understand the Server**

**Coding (30 min):**
1. Open [`server.py`](file:///Users/kritishpoptani/VT_PROJECT/src/api/server.py)
2. Trace the WebSocket loop (lines 90-192) step by step
3. Answer these on paper:
   - What happens when a frame arrives?
   - What does `max_avg_liveness` do and why?
   - Why is the bbox expanded by 40%?
4. Write comments on each section in your own words (actually edit the file!)

**Commute:**
- Watch: "What are WebSockets?" by Fireship or any short explainer
- Google: "FastAPI WebSocket tutorial" — just read, don't code yet

---

## 📅 Thursday, Sep 18

### Theme: **Python Fundamentals Checkup**

**Coding (30 min):**
1. Open a new Python file in VT_PROJECT called `practice/day1.py`
2. Write these from scratch (NO AI, NO Google):
   - A function that takes a list and returns the second largest number
   - A class `Student` with name, roll_number, and a method `display()`
   - Read a dictionary, loop through it, print key-value pairs
3. If stuck — struggle for 5 mins, then ask me to explain (not write)

**Commute:**
- Watch: "Python OOP in 15 minutes" (any YouTube video)
- Think: Can you explain what a class, object, constructor, and method are?

---

## 📅 Friday, Sep 19

### Theme: **Your First DSA Problem**

**Coding (30 min):**
1. Go to [leetcode.com](https://leetcode.com) → Create account if you don't have one
2. Solve: **"Two Sum"** (Problem #1) — the easiest problem on LeetCode
3. Try for 15-20 mins yourself first
4. If stuck, look at the hint, NOT the solution
5. After solving, write the solution again from scratch without looking

**Commute:**
- Watch: "How to start LeetCode as a beginner" (any short video)
- Think about: What is a HashMap/Dictionary and why is it useful?

---

## 📅 Saturday, Sep 20

### Theme: **Build Something Small (Part 1)**

**Coding (45 min):**
1. Create a new folder: `~/my_projects/todo_api/`
2. Build a simple **To-Do List API** with FastAPI — from scratch:
   - `POST /todos` — add a todo
   - `GET /todos` — list all todos
   - Store in a simple Python list (no database yet)
3. Write every line yourself. If stuck on FastAPI syntax, ask me to explain

**Commute:**
- Watch: "FastAPI crash course for beginners" (first 15 mins only)

---

## 📅 Sunday, Sep 21

### Theme: **Build Something Small (Part 2)**

**Coding (45 min):**
1. Continue the To-Do API:
   - Add `DELETE /todos/{id}` — delete a todo
   - Add `PUT /todos/{id}` — update a todo
2. Test it using your browser at `localhost:8000/docs` (FastAPI auto-generates Swagger UI!)
3. Push it to a NEW GitHub repo: `kritishp/todo-api`

**Commute:**
- Reflect: Compare your To-Do API with HoloSecure's server.py. What's similar? What's different?

---

## 📅 Monday, Sep 22

### Theme: **Review Week + Plan Next**

**Coding (30 min):**
1. Open your To-Do API and HoloSecure side by side
2. Write down 5 things you learned this week in a `LEARNINGS.md` file
3. Solve LeetCode Problem #2: **"Valid Parentheses"** (Stack concept)
4. Push everything to GitHub

**Commute:**
- Think: What do you want to learn next week?
- Options: React frontend, Database (SQLite/PostgreSQL), or more DSA

---

## 📊 Weekly Scorecard

Track yourself honestly. Put a ✅ or ❌ each day:

| Day | Did 30 min? | Commute learning? | Pushed to GitHub? |
|-----|------------|-------------------|-------------------|
| Tue | | | |
| Wed | | | |
| Thu | | | |
| Fri | | | |
| Sat | | | |
| Sun | | | |
| Mon | | | |

> [!IMPORTANT]
> **The goal this week is NOT to become an expert. The goal is to build the HABIT of daily practice.** If you complete even 5 out of 7 days, you've won.

---

## 🚫 Rules For This Week

1. **No copy-pasting AI code.** Ask AI to explain. Write code yourself.
2. **No skipping 2 days in a row.** One day off is fine. Two is a pattern.
3. **Push to GitHub every day you code.** Even if it's 5 lines. Green squares matter.
4. **Don't compare with your friend.** This week is about YOU.
