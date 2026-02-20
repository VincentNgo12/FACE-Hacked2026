# ElectroDysfunction – Hackathon 2026 Robot Platform  
A modular robotics framework built for the Hacked 2026 Hackathon.  
This project integrates computer vision, servo control, text-to-speech, and LLM-driven intelligence into a single, flexible robot platform.

Because the hackathon problem statement is unknown, the system is designed to be:
- **Modular** — each component can run independently  
- **Swappable** — Python or C++ vision, different LLM APIs, different hardware  
- **Hackathon-friendly** — fast to test, simple to integrate  

---


---

## 🧠 **Core Idea**

The robot runs five major subsystems:

1. **Vision Module**  
   - Captures camera frames  
   - Runs basic CV for target tracking  
   - Sends `(x, y)` target positions via IPC  

2. **LLM Module**  
   - Periodically sends frames to an LLM  
   - Receives structured outputs (direction, actions, comments)  
   - Used for commentary + “StudyBuddy personality”  

3. **Servo Module**  
   - Smooth motion control for pan/tilt  
   - Real-time tracking loop for targets detected by CV  
   - Exposes simple commands:  
     - `move_head(x, y)`  
     - `look_left()`, `look_right()`, `nod()`  

4. **TTS Module**  
   - Converts LLM text into audio  
   - Plays through USB or Pi audio  

5. **Orchestrator**  
   - Central “brainstem”  
   - Receives messages from CV  
   - Schedules LLM calls  
   - Triggers servos and audio  
   - Maintains robot state machine  

---

## 🚀 Getting Started

### 1. Install Python Dependencies  

---

## 🧠 **Core Idea**

The robot runs five major subsystems:

1. **Vision Module**  
   - Captures camera frames  
   - Runs basic CV for target tracking  
   - Sends `(x, y)` target positions via IPC  

2. **LLM Module**  
   - Periodically sends frames to an LLM  
   - Receives structured outputs (direction, actions, comments)  
   - Used for commentary + “StudyBuddy personality”  

3. **Servo Module**  
   - Smooth motion control for pan/tilt  
   - Real-time tracking loop for targets detected by CV  
   - Exposes simple commands:  
     - `move_head(x, y)`  
     - `look_left()`, `look_right()`, `nod()`  

4. **TTS Module**  
   - Converts LLM text into audio  
   - Plays through USB or Pi audio  

5. **Orchestrator**  
   - Central “brainstem”  
   - Receives messages from CV  
   - Schedules LLM calls  
   - Triggers servos and audio  
   - Maintains robot state machine  

---

## 🚀 Getting Started

### 1. Install Python Dependencies  
---

## 🧠 **Core Idea**

The robot runs five major subsystems:

1. **Vision Module**  
   - Captures camera frames  
   - Runs basic CV for target tracking  
   - Sends `(x, y)` target positions via IPC  

2. **LLM Module**  
   - Periodically sends frames to an LLM  
   - Receives structured outputs (direction, actions, comments)  
   - Used for commentary + “StudyBuddy personality”  

3. **Servo Module**  
   - Smooth motion control for pan/tilt  
   - Real-time tracking loop for targets detected by CV  
   - Exposes simple commands:  
     - `move_head(x, y)`  
     - `look_left()`, `look_right()`, `nod()`  

4. **TTS Module**  
   - Converts LLM text into audio  
   - Plays through USB or Pi audio  

5. **Orchestrator**  
   - Central “brainstem”  
   - Receives messages from CV  
   - Schedules LLM calls  
   - Triggers servos and audio  
   - Maintains robot state machine  

---

## 👥 Team Workflow

- Each subteam develops inside their module folder  
- Avoid cross-dependence between modules  
- Integration happens through IPC only  
- The orchestrator is the only module that sees everything  

---

## 📄 License
Internal Hackathon 2026 project — no external license yet.
