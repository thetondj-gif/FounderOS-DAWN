/**
 * Single source of truth for the app's primary navigation.
 */
import {
  Stethoscope,
  Home,
  MessageSquare,
  Share2,
  Clapperboard,
  Users,
  ListChecks,
  Sparkles,
  Network,
  Brain,
  Wallet,
  Filter,
  Workflow,
  Map,
  Plug,
  BarChart3,
  LayoutGrid,
  Layers,
  TerminalSquare,
} from 'lucide-react';

export type NavItem = { href: string; label: string; icon: typeof Home };

export const NAV_OPERATE: NavItem[] = [
  { href: '/founder', label: 'Founder Command', icon: TerminalSquare },
  { href: '/', label: 'Home', icon: Home },
  { href: '/comms', label: 'Comms', icon: MessageSquare },
  { href: '/funnel', label: 'Funnel', icon: Filter },
  { href: '/workflows', label: 'Workflows', icon: Workflow },
  { href: '/social', label: 'Social', icon: Share2 },
  { href: '/content', label: 'Content', icon: Clapperboard },
  { href: '/finances', label: 'Finances', icon: Wallet },
];

export const NAV_AGENTS: NavItem[] = [
  { href: '/agents', label: 'Agents', icon: Users },
  { href: '/tasks', label: 'Tasks', icon: ListChecks },
  { href: '/skills', label: 'Skills', icon: Sparkles },
  { href: '/org', label: 'Org Chart', icon: Network },
];

export const NAV_INTELLIGENCE: NavItem[] = [
  { href: '/brain', label: 'G-Brain', icon: Brain },
  { href: '/doctor', label: 'Doctor', icon: Stethoscope },
];

export const NAV_SYSTEM: NavItem[] = [
  { href: '/integrations', label: 'Connections', icon: Plug },
  { href: '/roadmap', label: 'Roadmap', icon: Map },
  { href: '/analytics', label: 'Analytics', icon: BarChart3 },
  { href: '/reference', label: 'Reference Model', icon: LayoutGrid },
];

export const NAV_LIBRARY: NavItem[] = [{ href: '/personas', label: 'Personas', icon: Layers }];

export const NAV_ORDER: string[] = [
  ...NAV_OPERATE,
  ...NAV_AGENTS,
  ...NAV_INTELLIGENCE,
  ...NAV_SYSTEM,
  ...NAV_LIBRARY,
].map((n) => n.href);

export const DIGIT_VIEWS: string[] = NAV_ORDER.slice(0, 9);
