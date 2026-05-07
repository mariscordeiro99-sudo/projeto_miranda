import React, { useState } from 'react';
import { useRegister } from '../hooks/useRegister';
import { useProfileImage } from '../hooks/useProfileImage';
import type { RegisterFormData } from '../types/registerForm';
import '../style/Register.css';

const Register: React.FC = () => {
    const [isLoading, setIsLoading] = useState(false);

    const {
        password, setPassword, rules, isPasswordValid,
        phone, handlePhoneChange
    } = useRegister();

    const {
        profileImage, imagePreview, handleImageChange
    } = useProfileImage();

    const [formData, setFormData] = useState({
        nome: '',
        email: '',
        usuario: '',
        isGestor: false
    });

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!isPasswordValid || isLoading) {
            return;
        }

        setIsLoading(true);

        const completeData: RegisterFormData = {
            nome: formData.nome,
            email: formData.email,
            usuario: formData.usuario,
            telefone: phone,
            senha: password,
            isGestor: formData.isGestor,
            fotoPerfil: profileImage
        };

        try {
            const data = new FormData();
            data.append('nome', completeData.nome);
            data.append('email', completeData.email);
            data.append('usuario', completeData.usuario);
            data.append('telefone', completeData.telefone);
            data.append('senha', completeData.senha);
            data.append('isGestor', String(completeData.isGestor));

            if (completeData.fotoPerfil) {
                data.append('fotoPerfil', completeData.fotoPerfil);
            }

            await new Promise(resolve => setTimeout(resolve, 2000));
            alert('Cadastro realizado com sucesso!');

        } catch (error) {
            console.error('Erro:', error);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="register-screen">
            <div className="register-card">
                <h2 className="register-title">Criar Nova Conta</h2>

                <form className="register-form" onSubmit={handleSubmit}>

                    <div className="form-group-photo">
                        <label htmlFor="photo-input" className="photo-label">
                            <div className="photo-circle">
                                {imagePreview ? (
                                    <img src={imagePreview} alt="Preview" />
                                ) : (
                                    <span className="photo-plus">+</span>
                                )}
                            </div>
                            <span className="photo-label-text">Foto de Perfil</span>
                        </label>
                        <input
                            id="photo-input"
                            type="file"
                            accept="image/*"
                            onChange={handleImageChange}
                            className="hidden-input"
                            disabled={isLoading}
                        />
                    </div>

                    <div className="form-row">
                        <div className="form-group">
                            <label>Nome Completo</label>
                            <input
                                type="text"
                                name="nome"
                                className="form-input"
                                placeholder="Ex: Carlos Alberto"
                                value={formData.nome}
                                onChange={handleInputChange}
                                required
                                disabled={isLoading}
                            />
                        </div>

                        <div className="form-group">
                            <label>Nome de Usuário</label>
                            <input
                                type="text"
                                name="usuario"
                                className="form-input"
                                placeholder="@carlos_dev"
                                value={formData.usuario}
                                onChange={handleInputChange}
                                required
                                disabled={isLoading}
                            />
                        </div>
                    </div>

                    <div className="form-row">
                        <div className="form-group">
                            <label>E-mail</label>
                            <input
                                type="email"
                                name="email"
                                className="form-input"
                                placeholder="nome@dominio.com"
                                value={formData.email}
                                onChange={handleInputChange}
                                required
                                disabled={isLoading}
                            />
                        </div>

                        <div className="form-group">
                            <label>Telefone</label>
                            <input
                                type="text"
                                className="form-input"
                                placeholder="(00) 00000-0000"
                                value={phone}
                                onChange={handlePhoneChange}
                                required
                                disabled={isLoading}
                            />
                        </div>
                    </div>

                    <div className="form-group">
                        <label>Senha Segura</label>
                        <input
                            type="password"
                            className="form-input"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            disabled={isLoading}
                        />

                        <div className="password-hints">
                            <span className={rules.length ? 'valid' : 'invalid'}>6-15 caracteres</span>
                            <span className={rules.upper ? 'valid' : 'invalid'}>Maiúscula</span>
                            <span className={rules.number ? 'valid' : 'invalid'}>Número</span>
                            <span className={rules.special ? 'valid' : 'invalid'}>Símbolo</span>
                        </div>
                    </div>

                    <div className="form-group">
                        <label>Nível de Acesso</label>
                        <select
                            name="isGestor"
                            className="form-input"
                            value={String(formData.isGestor)}
                            onChange={(e) => setFormData(p => ({ ...p, isGestor: e.target.value === 'true' }))}
                            disabled={isLoading}
                        >
                            <option value="false">Colaborador</option>
                            <option value="true">Gestor (Administrador)</option>
                        </select>
                    </div>

                    <button
                        type="submit"
                        className={`btn-register-submit ${isLoading ? 'loading' : ''}`}
                        disabled={!isPasswordValid || isLoading}
                    >
                        {isLoading ? 'Processando...' : 'Finalizar Cadastro'}
                    </button>
                </form>
            </div>
        </div>
    );
};

export default Register;