import { createContext } from "react";
import type { AuthContextType } from "./AuthTypes";
export const AuthContext = createContext<AuthContextType | undefined>(undefined);