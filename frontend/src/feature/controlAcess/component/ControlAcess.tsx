import React from 'react';
import { Shield, Search, User, Save } from 'lucide-react';
import { useControleAcesso } from '../hook/useControlAcess';
import '../style/controlAcess.css';

export const AccessControlPage: React.FC = () => {
    const { usuarios, busca, setBusca, isLoading, alternarPermissao, salvarAcessoUsuario } = useControleAcesso();

    return (
        <main className="access-container">
            <header className="access-header">
                <div className="header-title-wrapper">
                    <Shield size={28} color="#4169E1" />
                    <div>
                        <h2>Controle de Níveis de Acesso</h2>
                        <p>Gerencie as permissões de visualização e atribua perfis administrativos aos colaboradores.</p>
                    </div>
                </div>

                <div className="access-search-bar">
                    <Search size={18} color="#94a3b8" />
                    <input
                        type="text"
                        placeholder="Buscar por nome ou e-mail..."
                        value={busca}
                        onChange={(e) => setBusca(e.target.value)}
                    />
                </div>
            </header>

            <section className="access-card-panel">
                {isLoading ? (
                    <div className="access-loading-state">Carregando usuários cadastrados...</div>
                ) : usuarios.length === 0 ? (
                    <div className="access-empty-state">Nenhum colaborador encontrado com os critérios digitados.</div>
                ) : (
                    <div className="access-table-responsive">
                        <table className="access-table">
                            <thead>
                                <tr>
                                    <th>Colaborador</th>
                                    <th className="text-center">Controle de Acesso</th>
                                    <th className="text-center">Edição de Anúncios</th>
                                    <th className="text-center">Identificação Visual</th>
                                    <th className="text-center">Painel do Gestor</th> {/* 🆕 Cabeçalho adicionado */}
                                    <th className="text-center">Administrador (Total)</th>
                                    <th className="text-right">Ação</th>
                                </tr>
                            </thead>
                            <tbody>
                                {usuarios.map((usuario) => (
                                    <tr key={usuario.id} className={usuario.permissoes.isAdmin ? 'row-admin-highlight' : ''}>
                                        <td>
                                            <div className="user-profile-cell">
                                                {usuario.foto ? (
                                                    <img src={usuario.foto} alt={usuario.nome} className="user-cell-avatar" />
                                                ) : (
                                                    <div className="user-cell-placeholder">
                                                        <User size={16} color="#64748b" />
                                                    </div>
                                                )}
                                                <div className="user-cell-info">
                                                    <span className="user-cell-name">{usuario.nome}</span>
                                                    <span className="user-cell-email">{usuario.email}</span>
                                                </div>
                                            </div>
                                        </td>

                                        <td className="text-center">
                                            <label className="checkbox-custom-container">
                                                <input
                                                    type="checkbox"
                                                    checked={usuario.permissoes.controlAcess}
                                                    disabled={usuario.permissoes.isAdmin}
                                                    onChange={() => alternarPermissao(usuario.id, 'controlAcess')}
                                                />
                                                <span className="checkmark"></span>
                                            </label>
                                        </td>

                                        <td className="text-center">
                                            <label className="checkbox-custom-container">
                                                <input
                                                    type="checkbox"
                                                    checked={usuario.permissoes.announcement}
                                                    disabled={usuario.permissoes.isAdmin}
                                                    onChange={() => alternarPermissao(usuario.id, 'announcement')}
                                                />
                                                <span className="checkmark"></span>
                                            </label>
                                        </td>

                                        <td className="text-center">
                                            <label className="checkbox-custom-container">
                                                <input
                                                    type="checkbox"
                                                    checked={usuario.permissoes.idtVisual}
                                                    disabled={usuario.permissoes.isAdmin}
                                                    onChange={() => alternarPermissao(usuario.id, 'idtVisual')}
                                                />
                                                <span className="checkmark"></span>
                                            </label>
                                        </td>

                                        {/* 🆕 Coluna com a caixa de seleção do Painel do Gestor */}
                                        <td className="text-center">
                                            <label className="checkbox-custom-container">
                                                <input
                                                    type="checkbox"
                                                    checked={usuario.permissoes.dashboardGestor}
                                                    disabled={usuario.permissoes.isAdmin}
                                                    onChange={() => alternarPermissao(usuario.id, 'dashboardGestor')}
                                                />
                                                <span className="checkmark"></span>
                                            </label>
                                        </td>

                                        <td className="text-center">
                                            <label className="checkbox-custom-container admin-checkbox">
                                                <input
                                                    type="checkbox"
                                                    checked={usuario.permissoes.isAdmin}
                                                    onChange={() => alternarPermissao(usuario.id, 'isAdmin')}
                                                />
                                                <span className="checkmark checkmark-admin"></span>
                                            </label>
                                        </td>

                                        <td className="text-right">
                                            <button
                                                className="save-access-btn"
                                                onClick={() => salvarAcessoUsuario(usuario.id)}
                                                aria-label={`Salvar permissões de ${usuario.nome}`}
                                            >
                                                <Save size={16} />
                                                <span>Salvar</span>
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </section>
        </main>
    );
};