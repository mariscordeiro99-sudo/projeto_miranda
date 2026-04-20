import React, { useState, type ChangeEvent } from "react";

type AuthContextType = {
    user: string;
    setUser: React.Dispatch<React.SetStateAction<string>>;
    password: string;
    setPassword: React.Dispatch<React.SetStateAction<string>>;
    handleUserChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
    handlePasswordChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
    userError: string;
    passwordError: string;
};

export const useAuth = (): AuthContextType => {
    const [user, setUser] = useState("");
    const [password, setPassword] = useState("");
    const [userError, setUserError] = useState("");
    const [passwordError, setPasswordError] = useState("");

    const handleUserChange = (e: ChangeEvent<HTMLInputElement>) => { 
        const value = e.target.value;

        if (/\s/.test(value)) {
            setUserError("O usuário não pode conter espaços.");
        } else if (value.length > 15) {
            setUserError("Máximo de 15 caracteres.");
        } else {
            setUserError("");
        }
        const sanitizedValue = value.replace(/\s/g, "").substring(0, 15);

        setUser(sanitizedValue);
    };

    const handlePasswordChange = (e: ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value;

        const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!%*?&#]{0,}$/;

        if (value.length > 0 && value.length < 6) {
            setPasswordError("A senha deve ter no mínimo 6 caracteres.");
        } else if (value.length > 15) {
            setPasswordError("A senha deve ter no máximo 15 caracteres.");
        } else if (value.length > 0 && !passwordRegex.test(value)) {
            setPasswordError("Use pelo menos uma letra minúscula, uma letra maiúscula, um número e um caractere especial.");
        } else {
            setPasswordError("");
        }
        setPassword(value.substring(0, 15));
    };

    return {
        user,
        setUser, 
        password, 
        setPassword, 
        handleUserChange, 
        userError, 
        handlePasswordChange, 
        passwordError
    };
};