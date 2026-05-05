import React from "react";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement>{
    isLoading?: boolean;
    contentBtn?: string;
    classSpan?: string;
    classBtn?: string;
}

export const Button: React.FC<ButtonProps> = ({ isLoading, contentBtn, classSpan, classBtn, ...rest }) => {
    return (
        <button {...rest} disabled={isLoading || rest.disabled} className={classBtn}>
            <span className={classSpan}>
                {isLoading ? "Carregando..." : (contentBtn)}
            </span>
        </button>
    );
};