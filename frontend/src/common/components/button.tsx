import React from "react";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement>{
    isLoading?: boolean;
    content?: string;
    classSpan?: string;
    classBtn?: string;
}

export const Button: React.FC<ButtonProps> = ({ isLoading, children, content, classSpan, classBtn, ...rest }) => {
    return (
        <button {...rest} disabled={isLoading || rest.disabled} className={classBtn}>
            <span className={classSpan}>
                {isLoading ? "Carregando..." : (content || children)}
            </span>
        </button>
    );
};