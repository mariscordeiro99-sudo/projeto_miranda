import type { ChangeEvent, Dispatch, SetStateAction } from "react";

export interface AuthContextType {
    user: string;
    setUser: Dispatch<SetStateAction<string>>;
    password: string;
    setPassword: Dispatch<SetStateAction<string>>;
    handleUserChange: (e: ChangeEvent<HTMLInputElement>) => void;
    handlePasswordChange: (e: ChangeEvent<HTMLInputElement>) => void;
    userError: string;
    passwordError: string;
}