import React, { useState } from "react";

type LoginBtnProps = {
    user: string;
    password: string;
    hasErrors: boolean;
};

export const useLoginBtn = ({ user, password, hasErrors }: LoginBtnProps) => {
    const [isLoading, setIsLoading] = useState(false);

    const handleLoginSubmit = async (e: React.BaseSyntheticEvent) => {
        e.preventDefault();

        if (hasErrors || !user || !password) {
            console.error("Dados inválidos. Verifique os campos.");
            return;
        }

        setIsLoading(true);

        try {
            await new Promise((resolve) => setTimeout(resolve, 2000));
            console.log("Login efetuado para:", user);
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