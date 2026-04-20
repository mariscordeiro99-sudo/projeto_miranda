import React from "react";
import { Card } from "../../../common/components/Card";
import { Input } from "../../../common/components/Input";
import { Button } from "../../../common/components/Button";
import { useAuth } from "../hooks/Auth";

export const Login: React.FC = () => {
    const { user, 
            handleUserChange, 
            userError, 
            password, 
            handlePasswordChange, 
            passwordError
        } = useAuth();
    return (
        <Card
            title="Login"
            classCard="card"
            classCardHeader="card-header"
            classTitle="card-title"
            classCardContent="card-content"
            contentCard={
                <form className="login-form">
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
                        isLoading={false}
                        contentBtn="Entrar"
                        classSpan="login-btn-span"
                        classBtn="login-btn"
                    />
                </form>
            }
        />
    );
};