import React from "react";
import { Card } from "../../../common/components/Card";
import { Input } from "../../../common/components/Input";
import { Button } from "../../../common/components/Button";
import { useAuth } from "../hooks/Auth";
import { useLoginBtn } from "../hooks/LoginBtn";

export const Login: React.FC = () => {
    const { user, 
            handleUserChange, 
            userError, 
            password, 
            handlePasswordChange, 
            passwordError
        } = useAuth();

        const { isLoading, handleLoginSubmit } = useLoginBtn({
        user,
        password,
        hasErrors: !!userError || !!passwordError
    });
    return (
        <Card
            title="Login"
            classCard="card"
            classCardHeader="card-header"
            classTitle="card-title"
            classCardContent="card-content"
            contentCard={
                <form className="login-form" onSubmit={handleLoginSubmit}>
                    <Input
                        label="Usuário"
                        value={user}
                        onChange={handleUserChange}
                        error={userError}
                        classLabel="login-label"
                        classInput="login-input"
                    />
                    <Input
                        label="Senha"
                        value={password}
                        onChange={handlePasswordChange}
                        error={passwordError}
                        classLabel="login-label"
                        classInput="login-input"
                        type="password"
                    />
                    <Button
                        isLoading={isLoading}
                        contentBtn={isLoading ? "Entrando..." : "Entrar"}
                        classSpan="login-btn-span"
                        classBtn="login-btn"
                        disabled={isLoading || !!userError || !!passwordError || !user}
                    />
                </form>
            }
        />
    );
};