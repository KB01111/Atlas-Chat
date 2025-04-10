import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { FiAlertCircle, FiCheckCircle, FiCode, FiList, FiUserPlus, FiUsers } from 'react-icons/fi';
import CodeExecutionComponent from '../CodeExecution/CodeExecutionComponent';

const TeamChatInterface = ({
  teamId,
  messages = [],
  onSendMessage,
  onCreateCodingTask,
  onExecuteCode,
  onDownloadArtifact,
  onDeleteArtifact,
  agents = [],
  tasks = [],
  artifacts = [],
}) => {
  const { t } = useTranslation();
  const [messageInput, setMessageInput] = useState('');
  const [showCodeEditor, setShowCodeEditor] = useState(false);
  const [codeInput, setCodeInput] = useState('');
  const [selectedLanguage, setSelectedLanguage] = useState('python');
  const [selectedTask, setSelectedTask] = useState(null);
  const [showTaskDetails, setShowTaskDetails] = useState(false);
  const [taskArtifacts, setTaskArtifacts] = useState([]);

  useEffect(() => {
    if (selectedTask) {
      // Filter artifacts for the selected task
      const filteredArtifacts = artifacts.filter(
        (artifact) => artifact.metadata?.task_id === selectedTask.id,
      );
      setTaskArtifacts(filteredArtifacts);
    } else {
      setTaskArtifacts([]);
    }
  }, [selectedTask, artifacts]);

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (!messageInput.trim()) return;

    onSendMessage(messageInput);
    setMessageInput('');
  };

  const handleInputChange = (e) => {
    setMessageInput(e.target.value);
  };

  const toggleCodeEditor = () => {
    setShowCodeEditor(!showCodeEditor);
  };

  const handleCodeChange = (code) => {
    setCodeInput(code);
  };

  const handleLanguageChange = (language) => {
    setSelectedLanguage(language);
  };

  const handleExecuteCode = async () => {
    if (!codeInput.trim()) return;

    const result = await onExecuteCode(codeInput, selectedLanguage);
    return result;
  };

  const handleCreateCodingTask = () => {
    if (!codeInput.trim()) return;

    onCreateCodingTask({
      title: `Coding task in ${selectedLanguage}`,
      description: `Execute and optimize the following ${selectedLanguage} code`,
      language: selectedLanguage,
      code: codeInput,
    });

    setShowCodeEditor(false);
    setCodeInput('');
  };

  const handleTaskClick = (task) => {
    setSelectedTask(task);
    setShowTaskDetails(true);
  };

  const closeTaskDetails = () => {
    setShowTaskDetails(false);
    setSelectedTask(null);
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <FiCheckCircle className="status-icon completed" />;
      case 'failed':
        return <FiAlertCircle className="status-icon failed" />;
      case 'in_progress':
        return (
          <div className="status-icon in-progress">
            <div className="spinner" />
          </div>
        );
      default:
        return <div className="status-icon pending" />;
    }
  };

  const getAgentName = (agentId) => {
    const agent = agents.find((a) => a.id === agentId);
    return agent ? agent.name : 'Unknown Agent';
  };

  return (
    <div className="team-chat-interface">
      <div className="team-chat-sidebar">
        <div className="team-members-section">
          <div className="section-header">
            <FiUsers className="section-icon" />
            <h3>{t('Team Members')}</h3>
          </div>
          <div className="team-members-list">
            {agents.map((agent) => (
              <div key={agent.id} className="team-member-item">
                <div className="member-avatar">{agent.role === 'supervisor' ? 'S' : 'C'}</div>
                <div className="member-info">
                  <div className="member-name">{agent.name}</div>
                  <div className="member-role">{agent.role}</div>
                </div>
              </div>
            ))}
            <button className="add-member-button">
              <FiUserPlus className="icon" />
              {t('Add Agent')}
            </button>
          </div>
        </div>

        <div className="tasks-section">
          <div className="section-header">
            <FiList className="section-icon" />
            <h3>{t('Tasks')}</h3>
          </div>
          <div className="tasks-list">
            {tasks.map((task) => (
              <div
                key={task.id}
                className={`task-item ${selectedTask?.id === task.id ? 'selected' : ''}`}
                onClick={() => handleTaskClick(task)}
              >
                <div className="task-status">{getStatusIcon(task.status)}</div>
                <div className="task-info">
                  <div className="task-title">{task.title}</div>
                  <div className="task-assignee">{getAgentName(task.assigned_to)}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="team-chat-main">
        <div className="chat-messages">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`chat-message ${message.sender === 'user' ? 'user-message' : 'agent-message'}`}
            >
              <div className="message-sender">
                {message.sender === 'user' ? 'You' : getAgentName(message.sender)}
              </div>
              <div className="message-content">{message.content}</div>
              <div className="message-timestamp">
                {new Date(message.timestamp).toLocaleString()}
              </div>
            </div>
          ))}
        </div>

        <div className="chat-input-container">
          <form onSubmit={handleSendMessage}>
            <div className="chat-input-wrapper">
              <input
                type="text"
                className="chat-input"
                value={messageInput}
                onChange={handleInputChange}
                placeholder={t('Type a message...')}
              />
              <div className="chat-input-actions">
                <button
                  type="button"
                  className="icon-button code-button"
                  onClick={toggleCodeEditor}
                  title={t('Code Editor')}
                >
                  <FiCode />
                </button>
                <button type="submit" className="send-button" disabled={!messageInput.trim()}>
                  {t('Send')}
                </button>
              </div>
            </div>
          </form>
        </div>

        {showCodeEditor && (
          <div className="code-editor-modal">
            <div className="code-editor-modal-content">
              <CodeExecutionComponent
                initialCode={codeInput}
                language={selectedLanguage}
                onExecute={handleExecuteCode}
                onSave={handleCreateCodingTask}
                onArtifactDownload={onDownloadArtifact}
                onArtifactDelete={onDeleteArtifact}
              />
              <div className="code-editor-modal-actions">
                <button className="secondary-button" onClick={toggleCodeEditor}>
                  {t('Cancel')}
                </button>
                <button
                  className="primary-button"
                  onClick={handleCreateCodingTask}
                  disabled={!codeInput.trim()}
                >
                  {t('Create Coding Task')}
                </button>
              </div>
            </div>
          </div>
        )}

        {showTaskDetails && selectedTask && (
          <div className="task-details-modal">
            <div className="task-details-modal-content">
              <div className="task-details-header">
                <h2>{selectedTask.title}</h2>
                <button className="close-button" onClick={closeTaskDetails}>
                  &times;
                </button>
              </div>
              <div className="task-details-body">
                <div className="task-details-info">
                  <div className="task-detail-item">
                    <span className="detail-label">{t('Status')}:</span>
                    <span className={`detail-value status-${selectedTask.status}`}>
                      {selectedTask.status}
                    </span>
                  </div>
                  <div className="task-detail-item">
                    <span className="detail-label">{t('Assigned To')}:</span>
                    <span className="detail-value">{getAgentName(selectedTask.assigned_to)}</span>
                  </div>
                  <div className="task-detail-item">
                    <span className="detail-label">{t('Assigned By')}:</span>
                    <span className="detail-value">{getAgentName(selectedTask.assigned_by)}</span>
                  </div>
                  <div className="task-detail-item">
                    <span className="detail-label">{t('Priority')}:</span>
                    <span className={`detail-value priority-${selectedTask.priority}`}>
                      {selectedTask.priority}
                    </span>
                  </div>
                  <div className="task-detail-item">
                    <span className="detail-label">{t('Created')}:</span>
                    <span className="detail-value">
                      {new Date(selectedTask.created_at).toLocaleString()}
                    </span>
                  </div>
                </div>

                <div className="task-description">
                  <h3>{t('Description')}</h3>
                  <p>{selectedTask.description}</p>
                </div>

                {selectedTask.metadata?.language && (
                  <div className="task-code">
                    <h3>{t('Code')}</h3>
                    <CodeExecutionComponent
                      initialCode={selectedTask.metadata.initial_code || ''}
                      language={selectedTask.metadata.language}
                      readOnly={true}
                      showControls={false}
                    />
                  </div>
                )}

                {taskArtifacts.length > 0 && (
                  <div className="task-artifacts">
                    <h3>{t('Artifacts')}</h3>
                    <div className="artifacts-grid">
                      {taskArtifacts.map((artifact) => (
                        <div key={artifact.id} className="artifact-card">
                          <div className="artifact-card-header">
                            <div className="artifact-name">{artifact.name}</div>
                          </div>
                          <div className="artifact-card-actions">
                            <button
                              className="icon-button"
                              onClick={() => onDownloadArtifact(artifact)}
                              title={t('Download')}
                            >
                              <FiDownload />
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TeamChatInterface;
