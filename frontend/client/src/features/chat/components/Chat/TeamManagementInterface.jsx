import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { FiSettings, FiUserCheck, FiUserPlus, FiUsers, FiUserX } from 'react-icons/fi';
import TeamChatInterface from './TeamChatInterface';

const TeamManagementInterface = ({
  teams = [],
  onCreateTeam,
  onAddAgent,
  onRemoveAgent,
  onSelectTeam,
  onSendMessage,
  onCreateCodingTask,
  onExecuteCode,
  onDownloadArtifact,
  onDeleteArtifact,
}) => {
  const { t } = useTranslation();
  const [selectedTeam, setSelectedTeam] = useState(null);
  const [showCreateTeamModal, setShowCreateTeamModal] = useState(false);
  const [showAddAgentModal, setShowAddAgentModal] = useState(false);
  const [teamName, setTeamName] = useState('');
  const [supervisorName, setSupervisorName] = useState('');
  const [agentName, setAgentName] = useState('');
  const [agentRole, setAgentRole] = useState('coder');
  const [agentLanguages, setAgentLanguages] = useState(['python']);
  const [availableLanguages, setAvailableLanguages] = useState([
    { value: 'python', label: 'Python' },
    { value: 'javascript', label: 'JavaScript' },
    { value: 'typescript', label: 'TypeScript' },
    { value: 'java', label: 'Java' },
    { value: 'cpp', label: 'C++' },
    { value: 'csharp', label: 'C#' },
    { value: 'go', label: 'Go' },
    { value: 'rust', label: 'Rust' },
    { value: 'ruby', label: 'Ruby' },
  ]);

  useEffect(() => {
    if (teams.length > 0 && !selectedTeam) {
      setSelectedTeam(teams[0]);
      onSelectTeam(teams[0].id);
    }
  }, [teams, selectedTeam, onSelectTeam]);

  const handleTeamSelect = (team) => {
    setSelectedTeam(team);
    onSelectTeam(team.id);
  };

  const handleCreateTeam = (e) => {
    e.preventDefault();
    if (!teamName.trim() || !supervisorName.trim()) return;

    onCreateTeam({
      name: teamName,
      supervisorName: supervisorName,
    });

    setTeamName('');
    setSupervisorName('');
    setShowCreateTeamModal(false);
  };

  const handleAddAgent = (e) => {
    e.preventDefault();
    if (!agentName.trim() || !selectedTeam) return;

    onAddAgent({
      teamId: selectedTeam.id,
      name: agentName,
      role: agentRole,
      languages: agentLanguages,
    });

    setAgentName('');
    setAgentRole('coder');
    setAgentLanguages(['python']);
    setShowAddAgentModal(false);
  };

  const handleRemoveAgent = (agentId) => {
    if (!selectedTeam) return;

    onRemoveAgent({
      teamId: selectedTeam.id,
      agentId: agentId,
    });
  };

  const toggleLanguage = (language) => {
    if (agentLanguages.includes(language)) {
      setAgentLanguages(agentLanguages.filter((lang) => lang !== language));
    } else {
      setAgentLanguages([...agentLanguages, language]);
    }
  };

  return (
    <div className="team-management-interface">
      <div className="teams-sidebar">
        <div className="teams-header">
          <h2>{t('Teams')}</h2>
          <button
            className="icon-button"
            onClick={() => setShowCreateTeamModal(true)}
            title={t('Create Team')}
          >
            <FiUserPlus />
          </button>
        </div>

        <div className="teams-list">
          {teams.map((team) => (
            <div
              key={team.id}
              className={`team-item ${selectedTeam?.id === team.id ? 'selected' : ''}`}
              onClick={() => handleTeamSelect(team)}
            >
              <div className="team-icon">
                <FiUsers />
              </div>
              <div className="team-info">
                <div className="team-name">{team.name}</div>
                <div className="team-members-count">
                  {Object.keys(team.agents).length} {t('members')}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="team-content">
        {selectedTeam ? (
          <>
            <div className="team-header">
              <h1>{selectedTeam.name}</h1>
              <div className="team-actions">
                <button
                  className="icon-button"
                  onClick={() => setShowAddAgentModal(true)}
                  title={t('Add Agent')}
                >
                  <FiUserPlus />
                </button>
                <button className="icon-button" title={t('Team Settings')}>
                  <FiSettings />
                </button>
              </div>
            </div>

            <TeamChatInterface
              teamId={selectedTeam.id}
              messages={selectedTeam.messages || []}
              onSendMessage={onSendMessage}
              onCreateCodingTask={onCreateCodingTask}
              onExecuteCode={onExecuteCode}
              onDownloadArtifact={onDownloadArtifact}
              onDeleteArtifact={onDeleteArtifact}
              agents={Object.values(selectedTeam.agents)}
              tasks={selectedTeam.tasks || []}
              artifacts={selectedTeam.artifacts || []}
            />
          </>
        ) : (
          <div className="no-team-selected">
            <FiUsers className="icon" />
            <h2>{t('Select a team or create a new one')}</h2>
            <button className="primary-button" onClick={() => setShowCreateTeamModal(true)}>
              {t('Create Team')}
            </button>
          </div>
        )}
      </div>

      {showCreateTeamModal && (
        <div className="modal">
          <div className="modal-content">
            <div className="modal-header">
              <h2>{t('Create New Team')}</h2>
              <button className="close-button" onClick={() => setShowCreateTeamModal(false)}>
                &times;
              </button>
            </div>
            <form onSubmit={handleCreateTeam}>
              <div className="form-group">
                <label htmlFor="team-name">{t('Team Name')}</label>
                <input
                  id="team-name"
                  type="text"
                  value={teamName}
                  onChange={(e) => setTeamName(e.target.value)}
                  placeholder={t('Enter team name')}
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="supervisor-name">{t('Supervisor Name')}</label>
                <input
                  id="supervisor-name"
                  type="text"
                  value={supervisorName}
                  onChange={(e) => setSupervisorName(e.target.value)}
                  placeholder={t('Enter supervisor name')}
                  required
                />
              </div>
              <div className="form-actions">
                <button
                  type="button"
                  className="secondary-button"
                  onClick={() => setShowCreateTeamModal(false)}
                >
                  {t('Cancel')}
                </button>
                <button
                  type="submit"
                  className="primary-button"
                  disabled={!teamName.trim() || !supervisorName.trim()}
                >
                  {t('Create')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showAddAgentModal && (
        <div className="modal">
          <div className="modal-content">
            <div className="modal-header">
              <h2>{t('Add Agent to Team')}</h2>
              <button className="close-button" onClick={() => setShowAddAgentModal(false)}>
                &times;
              </button>
            </div>
            <form onSubmit={handleAddAgent}>
              <div className="form-group">
                <label htmlFor="agent-name">{t('Agent Name')}</label>
                <input
                  id="agent-name"
                  type="text"
                  value={agentName}
                  onChange={(e) => setAgentName(e.target.value)}
                  placeholder={t('Enter agent name')}
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="agent-role">{t('Agent Role')}</label>
                <select
                  id="agent-role"
                  value={agentRole}
                  onChange={(e) => setAgentRole(e.target.value)}
                >
                  <option value="coder">{t('Coder')}</option>
                  <option value="reviewer">{t('Reviewer')}</option>
                  <option value="tester">{t('Tester')}</option>
                  <option value="researcher">{t('Researcher')}</option>
                  <option value="documenter">{t('Documenter')}</option>
                </select>
              </div>
              {agentRole === 'coder' && (
                <div className="form-group">
                  <label>{t('Programming Languages')}</label>
                  <div className="language-checkboxes">
                    {availableLanguages.map((lang) => (
                      <div key={lang.value} className="language-checkbox">
                        <input
                          type="checkbox"
                          id={`lang-${lang.value}`}
                          checked={agentLanguages.includes(lang.value)}
                          onChange={() => toggleLanguage(lang.value)}
                        />
                        <label htmlFor={`lang-${lang.value}`}>{lang.label}</label>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              <div className="form-actions">
                <button
                  type="button"
                  className="secondary-button"
                  onClick={() => setShowAddAgentModal(false)}
                >
                  {t('Cancel')}
                </button>
                <button
                  type="submit"
                  className="primary-button"
                  disabled={
                    !agentName.trim() || (agentRole === 'coder' && agentLanguages.length === 0)
                  }
                >
                  {t('Add')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default TeamManagementInterface;
