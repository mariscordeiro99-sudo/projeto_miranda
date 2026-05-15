export interface ProfileCardProps {
  isOpen: boolean;
  onClose: () => void;
  userName: string;
  userPhoto?: string;
  userRole: string;
  onLogout: () => void;
}