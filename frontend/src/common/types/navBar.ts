export interface NavBarData {
  userName: string;
  userPhoto?: string;
  brasaoUrl?: string;
}

export interface NavBarActions {
  onOpenMenu: () => void;
  onOpenProfile: () => void;
}

export type NavBarProps = NavBarData & NavBarActions;