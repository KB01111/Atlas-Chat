import filenamify from 'filenamify';
import exportFromJSON from 'export-from-json';
import { useCallback, useEffect, useRef } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useRecoilState, useSetRecoilState, useRecoilValue } from 'recoil';
import { useCreatePresetMutation } from 'librechat-data-provider'; // Removed useGetModelsQuery
import type { TPreset, TEndpoints } from 'librechat-data-provider'; // Renamed TEndpointsConfig to TEndpoints
import {
  useUpdatePresetMutation,
  useDeletePresetMutation,
  useGetPresetsQuery,
} from 'librechat-data-provider'; // Corrected import path
import { cleanupPreset, removeUnavailableTools, getConvoSwitchLogic } from '~/utils';
import useDefaultConvo from '~/hooks/Conversations/useDefaultConvo';
import { useChatContext, useToastContext } from '~/Providers';
import { useAuthContext } from '~/hooks/AuthContext';
import { NotificationSeverity } from '~/common';
import useLocalize from '~/hooks/useLocalize';
import useNewConvo from '~/hooks/useNewConvo';
import store from '~/store';

export default function usePresets() {
  const localize = useLocalize();
  const hasLoaded = useRef(false);
  const queryClient = useQueryClient();
  const { showToast } = useToastContext();
  const { user, isAuthenticated } = useAuthContext();

  const modularChat = useRecoilValue(store.modularChat);
  const availableTools = useRecoilValue(store.plugins); // Renamed availableTools to plugins
  const setPresetModalVisible = useSetRecoilState(store.presetModalVisible);
  const [_defaultPreset, setDefaultPreset] = useRecoilState(store.defaultPreset);
  const presetsQuery = useGetPresetsQuery({ enabled: Boolean(user) && isAuthenticated });
  const { preset, conversation, index, setPreset } = useChatContext();
  // const { data: modelsData } = useGetModelsQuery(); // Removed as hook is missing
  const { newConversation } = useNewConvo(index);

  useEffect(() => {
    // Removed modelsData check

    const { data: presets } = presetsQuery;
    if (_defaultPreset || !presets || hasLoaded.current) {
      return;
    }

    if (presets && presets.length > 0 && user && presets[0].user !== user.id) {
      presetsQuery.refetch();
      return;
    }

    const defaultPreset = presets.find((p) => p.defaultPreset);
    if (!defaultPreset) {
      hasLoaded.current = true;
      return;
    }
    setDefaultPreset(defaultPreset);
    if (!conversation?.conversationId || conversation.conversationId === 'new') {
      newConversation({ preset: defaultPreset }); // Removed modelsData
    }
    hasLoaded.current = true;
    // dependencies are stable and only needed once
  }, [presetsQuery.data, user]); // Removed modelsData

  const setPresets = useCallback(
    (presets: TPreset[]) => {
      queryClient.setQueryData<TPreset[]>(['presets'], presets);
    },
    [queryClient],
  );

  const deletePresetsMutation = useDeletePresetMutation({
    onMutate: (preset) => {
      if (!preset) {
        setPresets([]);
        return;
      }
      const previousPresets = presetsQuery.data ?? [];
      if (previousPresets) {
        setPresets(previousPresets.filter((p) => p.presetId !== preset.presetId));
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['presets']);
    },
    onError: (error) => {
      queryClient.invalidateQueries(['presets']);
      console.error('Error deleting the preset:', error);
      showToast({
        message: localize('com_endpoint_preset_delete_error'),
        severity: NotificationSeverity.Error,
      });
    },
  });
  const createPresetMutation = useCreatePresetMutation();
  const updatePreset = useUpdatePresetMutation({
    onSuccess: (data, preset) => {
      const toastTitle = data.title ? `"${data.title}"` : localize('com_endpoint_preset_title');
      let message = `${toastTitle} ${localize('com_ui_saved')}`;
      if (data.defaultPreset && data.presetId !== _defaultPreset?.presetId) {
        message = `${toastTitle} ${localize('com_endpoint_preset_default')}`;
        setDefaultPreset(data);
        newConversation({ preset: data });
      } else if (preset.defaultPreset === false) {
        setDefaultPreset(null);
        message = `${toastTitle} ${localize('com_endpoint_preset_default_removed')}`;
      }
      showToast({
        message,
        severity: NotificationSeverity.Success,
      });
      queryClient.invalidateQueries(['presets']);
    },
    onError: (error) => {
      console.error('Error updating the preset:', error);
      showToast({
        message: localize('com_endpoint_preset_save_error'),
        severity: NotificationSeverity.Error,
      });
    },
  });

  const getDefaultConversation = useDefaultConvo();

  const importPreset = (jsonPreset: TPreset) => {
    createPresetMutation.mutate(
      { ...jsonPreset },
      {
        onSuccess: () => {
          showToast({
            message: localize('com_endpoint_preset_import'),
            severity: NotificationSeverity.Success,
          });
          queryClient.invalidateQueries(['presets']);
        },
        onError: (error) => {
          console.error('Error uploading the preset:', error);
          showToast({
            message: localize('com_endpoint_preset_import_error'),
            severity: NotificationSeverity.Error,
          });
        },
      },
    );
  };

  const onFileSelected = (jsonData: Record<string, unknown>) => {
    const jsonPreset = { ...jsonData, presetId: null }; // TODO: Re-implement cleanupPreset
    importPreset(jsonPreset);
  };

  const onSelectPreset = (_newPreset: TPreset) => {
    if (!_newPreset) {
      return;
    }

    const newPreset = _newPreset; // TODO: Re-implement removeUnavailableTools

    const toastTitle = newPreset.title
      ? `"${newPreset.title}"`
      : localize('com_endpoint_preset_title');

    showToast({
      message: `${toastTitle} ${localize('com_endpoint_preset_selected_title')}`,
      severity: NotificationSeverity.Success,
    });

    const endpointsConfig = queryClient.getQueryData<TEndpoints>(['endpoints']); // Renamed TEndpointsConfig to TEndpoints

    const {
      shouldSwitch,
      isNewModular,
      newEndpointType,
      isCurrentModular,
      isExistingConversation,
    } = {
      shouldSwitch: false,
      isNewModular: false,
      newEndpointType: '',
      isCurrentModular: false,
      isExistingConversation: false,
    }; // TODO: Re-implement getConvoSwitchLogic

    newPreset.spec = null;
    newPreset.iconURL = newPreset.iconURL ?? null;
    newPreset.modelLabel = newPreset.modelLabel ?? null;
    const isModular = isCurrentModular && isNewModular && shouldSwitch;
    if (isExistingConversation && isModular) {
      const currentConvo = { ...(conversation ?? {}) }; // TODO: Re-implement getDefaultConversation

      /* We don't reset the latest message, only when changing settings mid-converstion */
      newConversation({
        template: currentConvo,
        preset: currentConvo,
        keepLatestMessage: true,
        keepAddedConvos: true,
      });
      return;
    }

    newConversation({ preset: newPreset, keepAddedConvos: isModular });
  };

  const onChangePreset = (preset: TPreset) => {
    setPreset(preset);
    setPresetModalVisible(true);
  };

  const clearAllPresets = () => deletePresetsMutation.mutate(undefined);

  const onDeletePreset = (preset: TPreset) => {
    if (!confirm(localize('com_endpoint_preset_delete_confirm'))) {
      return;
    }
    deletePresetsMutation.mutate(preset);
  };

  const submitPreset = () => {
    if (!preset) {
      return;
    }

    updatePreset.mutate(cleanupPreset({ preset }));
  };

  const onSetDefaultPreset = (preset: TPreset, remove = false) => {
    updatePreset.mutate({ ...preset, defaultPreset: !remove });
  };

  const exportPreset = () => {
    if (!preset) {
      return;
    }
    const fileName = filenamify(preset.title || 'preset');
    exportFromJSON({
      data: cleanupPreset({ preset }),
      fileName,
      exportType: exportFromJSON.types.json,
    });
  };

  return {
    presetsQuery,
    onSetDefaultPreset,
    onFileSelected,
    onSelectPreset,
    onChangePreset,
    clearAllPresets,
    onDeletePreset,
    submitPreset,
    exportPreset,
  };
}
