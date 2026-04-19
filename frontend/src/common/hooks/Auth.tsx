import { useState } from "react";

type AuthContextType = {
    user: string;
    setUser: React.Dispatch<React.SetStateAction<string>>;
    password: string;
    setPassword: React.Dispatch<React.SetStateAction<string>>;
};

export const useAuth = () : AuthContextType => {
    const [user, setUser] = useState("");
    const [password, setPassword] = useState("");
    return { user, setUser, password, setPassword};
    };