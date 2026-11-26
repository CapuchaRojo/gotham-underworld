import { useEffect, useState } from "react";
import type { KeyboardEvent } from "react";
import { ScenarioSwitcher } from "./components/ScenarioSwitcher";
import { DeveloperModeToggle } from "./components/DeveloperModeToggle";
import { StreetsView } from "./components/StreetsView";
import { LifeView } from "./components/LifeView";
import { StoryView } from "./components/StoryView";
import { TodayView } from "./components/TodayView";
import { BookOpenIcon, CalendarIcon, MapIcon, WalletIcon } from "./components/icons";
import { PresentationModeProvider, usePresentationMode } from "./presentation";
import { GameplayProvider, useGameplay } from "./gameplay/GameplayProvider";

type TabId = "today" | "streets" | "life" | "story";

const TABS: { id: TabId; label: string; icon: typeof MapIcon }[] = [
  { id: "today", label: "Today", icon: CalendarIcon },
  { id: "streets", label: "The Streets", icon: MapIcon },
  { id: "life", label: "My Life", icon: WalletIcon },
  { id: "story", label: "My Story", icon: BookOpenIcon },
];

function AppShell() {
  const { isDeveloper } = usePresentationMode();
  const { scenario, engineStatus, selectScenario } = useGameplay();
  const [tab, setTab] = useState<TabId>("today");

  // Player mode always lands on the personal Today screen. Developer Inspection
  // opens on the diagnostic-heavy Streets view. Mode switches reset to the
  // appropriate landing view so player vs QA context never bleeds together.
  useEffect(() => {
    setTab(isDeveloper ? "streets" : "today");
  }, [isDeveloper]);

  function onTabsKeyDown(e: KeyboardEvent<HTMLDivElement>) {
    const idx = TABS.findIndex((t) => t.id === tab);
    if (e.key === "ArrowRight") {
      e.preventDefault();
      const next = TABS[(idx + 1) % TABS.length];
      setTab(next.id);
      document.getElementById(`tab-${next.id}`)?.focus();
    } else if (e.key === "ArrowLeft") {
      e.preventDefault();
      const next = TABS[(idx + TABS.length - 1) % TABS.length];
      setTab(next.id);
      document.getElementById(`tab-${next.id}`)?.focus();
    }
  }

  return (
    <div className="noir-texture flex min-h-screen flex-col text-foreground">
      <header className="sticky top-0 z-10 border-b border-border bg-background/90 backdrop-blur">
        <div className="mx-auto flex w-full max-w-6xl flex-col gap-3 px-4 py-3 sm:px-6">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <h1 className="font-heading text-xl font-bold leading-tight">Gotham: The Goon</h1>
              <p className="text-xs text-muted">Living Gotham Interface</p>
            </div>
            <div className="flex flex-col items-end gap-2">
              {isDeveloper ? (
                <ScenarioSwitcher activeId={scenario.id} onChange={selectScenario} />
              ) : null}
              <DeveloperModeToggle />
            </div>
          </div>
          <div
            className="flex flex-wrap items-center gap-2 rounded-md border border-border bg-surface px-3 py-1.5 text-[11px] text-muted"
            title={engineStatus.detail}
          >
            <span className="inline-block h-1.5 w-1.5 rounded-full bg-primary" />
            <span className="font-medium text-foreground">{engineStatus.label}</span>
            <span className="ml-auto inline-flex items-center gap-1.5 rounded border border-border px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-muted-strong">
              <span className="inline-block h-1 w-1 rounded-full bg-money" />
              {engineStatus.contextLabel}
            </span>
          </div>
        </div>

        <nav className="mx-auto w-full max-w-6xl px-4 sm:px-6">
          <div role="tablist" aria-label="Views" className="flex gap-1" onKeyDown={onTabsKeyDown}>
            {TABS.map((t) => {
              const active = tab === t.id;
              const Icon = t.icon;
              return (
                <button
                  key={t.id}
                  id={`tab-${t.id}`}
                  role="tab"
                  type="button"
                  aria-selected={active}
                  aria-controls={`panel-${t.id}`}
                  onClick={() => setTab(t.id)}
                  className={`-mb-px flex cursor-pointer items-center gap-1.5 border-b-2 px-3 py-2 text-sm font-medium transition-colors duration-200 ${
                    active
                      ? "border-primary text-primary"
                      : "border-transparent text-muted hover:text-foreground"
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  {t.label}
                </button>
              );
            })}
          </div>
        </nav>
      </header>

      <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-5 sm:px-6">
        <div role="tabpanel" id={`panel-${tab}`} aria-labelledby={`tab-${tab}`} tabIndex={0}>
          {tab === "today" ? (
            <TodayView scenario={scenario} onNavigate={setTab} showInteractionPreview />
          ) : tab === "streets" ? (
            <StreetsView scenario={scenario} />
          ) : tab === "life" ? (
            <LifeView scenario={scenario} />
          ) : (
            <StoryView scenario={scenario} />
          )}
        </div>
      </main>

      <footer className="border-t border-border bg-background/70">
        <div className="mx-auto flex w-full max-w-6xl flex-wrap items-center justify-between gap-2 px-4 py-3 text-[11px] text-muted sm:px-6">
          <span>Independent unofficial prototype.</span>
          <span>No persistence — refresh returns to Stable life.</span>
        </div>
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <PresentationModeProvider>
      <GameplayProvider>
        <AppShell />
      </GameplayProvider>
    </PresentationModeProvider>
  );
}
