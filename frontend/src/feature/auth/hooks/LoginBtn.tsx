import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/Auth";
import api from '../../../common/services/api';

type LoginBtnProps = {
    user: string;
    password: string;
    hasErrors: boolean;
};

export const useLoginBtn = ({ user, password, hasErrors }: LoginBtnProps) => {
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string>("");
    const navigate = useNavigate();
    const { setLoggedUser } = useAuth(); 

    const handleLoginSubmit = async (e: React.BaseSyntheticEvent) => {
        e.preventDefault();

        if (hasErrors || !user || !password) {
            setError("Dados inválidos. Verifique os campos.");
            return;
        }

        setIsLoading(true);
        setError("");

        try {
            const response = await api.post("/login", {
                username: user,
                password: password
            });

            const { token } = response.data;
            
            localStorage.setItem("token", token);
            setLoggedUser(user);

            console.log("Login efetuado para:", user);
            navigate("/home");

        } catch (err: unknown) {
            const errorMessage = axios.isAxiosError<{ detail?: string }>(err)
                ? err.response?.data?.detail || "Usuário ou senha inválidos."
                : "Não foi possível concluir o login.";
            setError(errorMessage);
            console.error("Erro ao fazer login:", err);
        } finally {
            setIsLoading(false);
        }
    };

    return {
        isLoading,
        error,
        handleLoginSubmit
    };
};
