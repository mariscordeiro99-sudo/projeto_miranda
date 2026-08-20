export interface ProfileCardProps {
  isOpen: boolean;
  onClose: () => void;
  userName: string;
  userPhoto: string | null | undefined;
  userRole: string;
  onLogout: () => void;
}