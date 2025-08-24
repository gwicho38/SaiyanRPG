# SaiyanQuest Architecture Diagram

## High-Level Architecture Overview

```mermaid
graph TB
    subgraph EP["Entry Points"]
        Main["main.py / __main__.py"]
    end
    
    subgraph CCL["Core Client Layer"]
        Client["LocalPygameClient<br/>Main Game Controller"]
        Session["Session<br/>Game State Container"]
    end
    
    subgraph STM["State Management"]
        SM["StateManager<br/>State Stack"]
        States["Game States"]
        StateFactory["State Factory"]
    end
    
    subgraph GS["Game States"]
        WorldState["WorldState<br/>Exploration"]
        CombatState["CombatState<br/>Battles"]
        MenuStates["Menu States<br/>UI Screens"]
        TransitionStates["Transitions<br/>Fade/Flash"]
    end
    
    subgraph ES["Event System"]
        EventEngine["Event Engine<br/>Scripting System"]
        Actions["100+ Actions<br/>Commands"]
        Conditions["Conditions<br/>Game Logic"]
    end
    
    subgraph GE["Game Entities"]
        Player["Player<br/>User Character"]
        NPC["NPCs<br/>AI Characters"]
        Monster["Monsters<br/>Creatures"]
    end
    
    subgraph MG["Managers"]
        MapManager["Map Manager"]
        NPCManager["NPC Manager"]
        MovementManager["Movement Manager"]
        CollisionManager["Collision Manager"]
        SoundManager["Sound Manager"]
        NetworkManager["Network Manager"]
    end
    
    subgraph DL["Data Layer"]
        DB["Database Models<br/>Pydantic"]
        Config["Configuration<br/>YAML/JSON"]
        Assets["Asset Management"]
    end
    
    Main --> Client
    Client --> Session
    Client --> SM
    SM --> States
    States --> StateFactory
    StateFactory --> WorldState
    StateFactory --> CombatState
    StateFactory --> MenuStates
    StateFactory --> TransitionStates
    
    Client --> EventEngine
    EventEngine --> Actions
    EventEngine --> Conditions
    
    Session --> Player
    Session --> NPC
    Session --> Monster
    
    Client --> MapManager
    Client --> NPCManager
    Client --> MovementManager
    Client --> CollisionManager
    Client --> SoundManager
    Client --> NetworkManager
    
    WorldState --> MapManager
    WorldState --> NPCManager
    WorldState --> MovementManager
    WorldState --> CollisionManager
    
    Monster --> DB
    NPC --> DB
    Config --> Client
    Assets --> Client
```

## Module Dependencies

```mermaid
graph LR
    subgraph CM["Core Modules"]
        client[client.py]
        session[session.py]
        state["state/"]
    end
    
    subgraph GL["Game Logic"]
        combat["combat/"]
        event["event/"]
        core["core/"]
    end
    
    subgraph ENT["Entities"]
        monster[monster.py]
        npc[npc.py]
        player[player.py]
    end
    
    subgraph GM["Game Mechanics"]
        item["item/"]
        technique["technique/"]
        status["status/"]
    end
    
    subgraph UIL["UI Layer"]
        ui["ui/"]
        menu["menu/"]
        sprite[sprite.py]
    end
    
    subgraph DC["Data & Config"]
        db[db.py]
        config[config.py]
        constants["constants/"]
    end
    
    client --> state
    client --> session
    session --> player
    player --> npc
    npc --> monster
    
    combat --> monster
    combat --> technique
    combat --> status
    
    event --> core
    event --> combat
    
    ui --> sprite
    menu --> ui
    
    monster --> db
    item --> db
    technique --> db
```

## Combat System Flow

```mermaid
sequenceDiagram
    participant W as WorldState
    participant E as EventEngine
    participant C as CombatState
    participant Q as ActionQueue
    participant M as Monsters
    participant R as Resolution
    
    W->>E: Trigger Battle Event
    E->>C: Initialize Combat
    C->>M: Load Combatants
    C->>Q: Setup Turn Order
    
    loop Battle Turns
        Q->>C: Get Next Action
        C->>M: Execute Action
        M->>R: Calculate Damage/Effects
        R->>M: Apply Changes
        M->>C: Update State
        C->>Q: Check Victory/Defeat
    end
    
    C->>W: Return to World
```

## State Management Pattern

```mermaid
stateDiagram-v2
    [*] --> StartScreen
    StartScreen --> MainMenu
    MainMenu --> WorldState
    MainMenu --> LoadGame
    
    WorldState --> CombatState: Battle Encounter
    WorldState --> MenuState: Open Menu
    WorldState --> DialogueState: NPC Interaction
    
    CombatState --> WorldState: Battle End
    CombatState --> GameOverState: Defeat
    
    MenuState --> WorldState: Close Menu
    DialogueState --> WorldState: End Dialogue
    
    GameOverState --> MainMenu: Restart
    LoadGame --> WorldState: Load Save
```

## Event System Architecture

```mermaid
graph TD
    subgraph "Event Processing"
        Input[User Input]
        MapEvent[Map Events]
        GameScript[Game Scripts]
    end
    
    subgraph "Event Engine"
        ConditionChecker[Condition Checker]
        ActionExecutor[Action Executor]
        EventBus[Event Bus]
    end
    
    subgraph "Actions (Sample)"
        Teleport[teleport]
        StartBattle[start_battle]
        AddMonster[add_monster]
        PlaySound[play_sound]
        ShowDialog[show_dialogue]
        ModifyVariable[set_variable]
    end
    
    subgraph "Conditions (Sample)"
        HasMonster[has_monster]
        VariableCheck[variable_is]
        PlayerAt[player_at]
        MonsterFainted[monster_fainted]
    end
    
    Input --> EventBus
    MapEvent --> EventBus
    GameScript --> EventBus
    
    EventBus --> ConditionChecker
    ConditionChecker --> Conditions
    
    ConditionChecker -->|Pass| ActionExecutor
    ActionExecutor --> Actions
    
    Actions --> GameState[Game State Updates]
```

## Key Design Patterns

| Pattern | Implementation | Purpose |
|---------|---------------|----------|
| **State Pattern** | StateManager, Game States | Manage different game screens |
| **Command Pattern** | Event Actions, Combat Queue | Encapsulate game actions |
| **Observer Pattern** | Event Bus, State Notifications | Decoupled communication |
| **Factory Pattern** | State Factory, Entity Creation | Object instantiation |
| **Repository Pattern** | State Repository, DB Models | Data access abstraction |
| **Manager Pattern** | Various Manager Classes | Subsystem management |
| **Plugin Architecture** | Dynamic Action/Condition Loading | Extensibility |

## Package Structure

```
saiyanquest/
├── __init__.py              # Package initialization
├── __main__.py              # CLI entry point
├── main.py                  # Main game entry
├── client.py                # Core game client
├── session.py               # Session management
├── config.py                # Configuration system
├── db.py                    # Database models
│
├── state/                   # State management system
│   ├── state_manager.py    # State stack management
│   ├── state.py            # Base state class
│   ├── state_factory.py    # State creation
│   └── state_repository.py # State registry
│
├── states/                  # Game state implementations
│   ├── world/              # World exploration
│   ├── combat/             # Battle system
│   ├── menu/               # Menu screens
│   └── transition/         # Screen transitions
│
├── event/                   # Event system
│   ├── eventengine.py      # Core event processor
│   ├── actions/            # 100+ action classes
│   └── conditions/         # Condition evaluators
│
├── combat/                  # Combat mechanics
│   ├── combat_state.py     # Battle management
│   ├── action_queue.py     # Turn management
│   └── damage.py           # Damage calculations
│
├── ui/                      # User interface
│   ├── combat_*.py         # Combat UI components
│   ├── text_*.py           # Text rendering
│   └── dialogue.py         # Dialogue system
│
├── core/                    # Core game logic
├── item/                    # Item system
├── technique/               # Move/ability system
├── status/                  # Status effects
├── menu/                    # Menu implementations
└── constants/               # Game constants
```

## Data Flow Overview

```mermaid
graph TD
    subgraph "Input Layer"
        KB[Keyboard Input]
        GP[Gamepad Input]
        NET[Network Input]
    end
    
    subgraph "Processing Layer"
        IM[Input Manager]
        EM[Event Manager]
        SM[State Manager]
    end
    
    subgraph "Game Logic"
        GS[Game States]
        EE[Event Engine]
        GL[Game Logic]
    end
    
    subgraph "Data Layer"
        SS[Session State]
        GD[Game Data]
        SV[Save System]
    end
    
    subgraph "Output Layer"
        REN[Renderer]
        SND[Sound System]
        NETOUT[Network Output]
    end
    
    KB --> IM
    GP --> IM
    NET --> IM
    
    IM --> EM
    EM --> SM
    SM --> GS
    
    GS --> EE
    EE --> GL
    GL --> SS
    
    SS --> GD
    GD --> SV
    
    GS --> REN
    GS --> SND
    GS --> NETOUT
```

This architecture demonstrates a well-structured, modular game design with clear separation of concerns, extensive use of design patterns, and a flexible event-driven system that allows for easy content creation and game expansion.