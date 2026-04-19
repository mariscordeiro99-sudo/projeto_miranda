import React from "react";
import { Card } from "../../../common/components/Card";
import { Input } from "../../../common/components/Input";
import { Button } from "../../../common/components/Button";
import { useAuth } from "../../../common/hooks/Auth";

export const Login: React.FC = () => {
    const { user, setUser, password, setPassword } = useAuth();

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
                        onChange={(e) => setUser(e.target.value)}
                        classLabel="login-label"
                        classInput="login-input"
                    />
                    <Input
                        label="Senha"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
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