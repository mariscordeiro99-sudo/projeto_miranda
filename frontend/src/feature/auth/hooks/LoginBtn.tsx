import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/Auth";

type LoginBtnProps = {
    user: string;
    password: string;
    hasErrors: boolean;
};

export const useLoginBtn = ({ user, password, hasErrors }: LoginBtnProps) => {
    const [isLoading, setIsLoading] = useState(false);
    const navigate = useNavigate();
    const { setLoggedUser } = useAuth(); 

    const handleLoginSubmit = async (e: React.BaseSyntheticEvent) => {
        e.preventDefault();

        if (hasErrors || !user || !password) {
            console.error("Dados inválidos. Verifique os campos.");
            return;
        }

        setIsLoading(true);

        try {
            await new Promise((resolve) => setTimeout(resolve, 2000));
            setLoggedUser(user);

            console.log("Login efetuado para:", user);

            navigate("/home");

        } catch (error) {
            console.error("Erro ao processar login:", error);
        } finally {
            setIsLoading(false);
        }
    };

    return {
        isLoading,
        handleLoginSubmit
    };
};