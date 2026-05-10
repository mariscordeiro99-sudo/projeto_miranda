import React from "react";
import { Card } from "../../../common/components/Card";
import { Input } from "../../../common/components/Input";
import { Button } from "../../../common/components/button";
import { useAuth } from "../hooks/Auth";
import { useLoginBtn } from "../hooks/LoginBtn";
import "../styles/login.css";

export const Login: React.FC = () => {
    const { user, 
            handleUserChange, 
            userError, 
            password, 
            handlePasswordChange, 
            passwordError
        } = useAuth();

        const { isLoading, error, handleLoginSubmit } = useLoginBtn({
        user,
        password,
        hasErrors: !!userError || !!passwordError
    });

    const getUserStatusClass = () => {
        if (!user) return "";
        return userError ? "input-error" : "input-success";
    };

    const getPasswordStatusClass = () => {
        if (!password) return "";
        return passwordError ? "input-error" : "input-success";
    };

    return (
        <Card
            title="Login"
            classCard="card"
            classCardHeader="card-header"
            classTitle="card-title"
            classCardContent="card-content"
            contentCard={
                <form className="login-form" onSubmit={handleLoginSubmit}>
                    {error && <div style={{ color: "red", marginBottom: "10px" }}>{error}</div>}
                    <div className="input-group">
                        <Input
                            label="Usuário"
                            value={user}
                            onChange={handleUserChange}
                            error={userError}
                            classLabel="login-label"
                            classInput={`login-input ${getUserStatusClass()}`}
                        />
                        {userError && <span className="tooltip-error">{userError}</span>}
                    </div>
                    <div className="input-group">
                        <Input
                            label="Senha"
                            value={password}
                            onChange={handlePasswordChange}
                            error={passwordError}
                            classLabel="login-label"
                            classInput={`login-input ${getPasswordStatusClass()}`}
                            type="password"
                        />
                        {passwordError && <span className="tooltip-error">{passwordError}</span>}
                    </div>

                    <div className="otherPage">
                        <p className="remember">Esqueceu a Senha?</p>
                        <p className="register">Cadastre-se Aqui</p>

                    </div>
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