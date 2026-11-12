import { lazy, Suspense, type ComponentType } from 'react';
import { Route, Routes } from 'react-router-dom';
import { Layout } from './components/Layout';
import { Spinner } from './components/ui';

const p = (f: () => Promise<any>, name: string) => lazy<ComponentType<any>>(() => f().then((m) => ({ default: m[name] })));

const Overview = p(() => import('./pages/Overview'), 'Overview');
const Roadmap = p(() => import('./pages/Roadmap'), 'Roadmap');
const Documentation = p(() => import('./pages/Documentation'), 'Documentation');
const GameDesign = p(() => import('./pages/GameDesign'), 'GameDesign');
const AgentsCenter = p(() => import('./pages/AgentsCenter'), 'AgentsCenter');
const AgentProfile = p(() => import('./pages/AgentProfile'), 'AgentProfile');
const Communication = p(() => import('./pages/Communication'), 'Communication');
const Workflows = p(() => import('./pages/Workflows'), 'Workflows');
const Workspace = p(() => import('./pages/Workspace'), 'Workspace');
const Explorer = p(() => import('./pages/Explorer'), 'Explorer');
const UIDevelopment = p(() => import('./pages/UIDevelopment'), 'UIDevelopment');
const Assets = p(() => import('./pages/Assets'), 'Assets');
const TaskBoard = p(() => import('./pages/TaskBoard'), 'TaskBoard');
const Approvals = p(() => import('./pages/Approvals'), 'Approvals');
const Testing = p(() => import('./pages/Testing'), 'Testing');
const Bugs = p(() => import('./pages/Bugs'), 'Bugs');
const Performance = p(() => import('./pages/Performance'), 'Performance');
const Builds = p(() => import('./pages/Builds'), 'Builds');
const ActivityLogs = p(() => import('./pages/ActivityLogs'), 'ActivityLogs');
const Integrations = p(() => import('./pages/Integrations'), 'Integrations');
const AIConfig = p(() => import('./pages/AIConfig'), 'AIConfig');
const SettingsPage = p(() => import('./pages/Settings'), 'SettingsPage');
const BrainOverview = p(() => import('./pages/brain/BrainOverview'), 'BrainOverview');
const KnowledgeSources = p(() => import('./pages/brain/KnowledgeSources'), 'KnowledgeSources');
const Decisions = p(() => import('./pages/brain/Decisions'), 'Decisions');
const ContextRetrieval = p(() => import('./pages/brain/ContextRetrieval'), 'ContextRetrieval');
const ChangeHistory = p(() => import('./pages/brain/ChangeHistory'), 'ChangeHistory');

export default function App() {
  return (
    <Suspense fallback={<Spinner />}>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<Overview />} />
          <Route path="roadmap" element={<Roadmap />} />
          <Route path="docs" element={<Documentation />} />
          <Route path="game-design" element={<GameDesign />} />
          <Route path="agents" element={<AgentsCenter />} />
          <Route path="agents/:id" element={<AgentProfile />} />
          <Route path="chat" element={<Communication />} />
          <Route path="workflows" element={<Workflows />} />
          <Route path="workspace" element={<Workspace mode="all" />} />
          <Route path="luau" element={<Workspace mode="luau" />} />
          <Route path="explorer" element={<Explorer />} />
          <Route path="ui" element={<UIDevelopment />} />
          <Route path="assets" element={<Assets kind="all" />} />
          <Route path="assets-3d" element={<Assets kind="3d" />} />
          <Route path="tasks" element={<TaskBoard />} />
          <Route path="approvals" element={<Approvals />} />
          <Route path="testing" element={<Testing />} />
          <Route path="bugs" element={<Bugs />} />
          <Route path="performance" element={<Performance />} />
          <Route path="builds" element={<Builds />} />
          <Route path="logs" element={<ActivityLogs />} />
          <Route path="integrations" element={<Integrations />} />
          <Route path="ai-config" element={<AIConfig />} />
          <Route path="settings" element={<SettingsPage />} />
          <Route path="brain" element={<BrainOverview />} />
          <Route path="brain/sources" element={<KnowledgeSources />} />
          <Route path="brain/canonical" element={<Documentation canonicalOnly />} />
          <Route path="brain/decisions" element={<Decisions />} />
          <Route path="brain/context" element={<ContextRetrieval />} />
          <Route path="brain/history" element={<ChangeHistory />} />
          <Route path="*" element={<div className="py-20 text-center text-mute">Nie znaleziono strony.</div>} />
        </Route>
      </Routes>
    </Suspense>
  );
}
