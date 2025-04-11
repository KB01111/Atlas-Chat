import { useRecoilValue } from 'recoil';

import { TTSEndpoints } from '~/common';
import {
  EdgeVoiceDropdown,
  BrowserVoiceDropdown,
  ExternalVoiceDropdown,
} from '~/components/Audio/Voices';
import store from '~/store';

const voiceDropdownComponentsMap = {
  [TTSEndpoints.edge]: EdgeVoiceDropdown,
  [TTSEndpoints.browser]: BrowserVoiceDropdown,
  [TTSEndpoints.external]: ExternalVoiceDropdown,
};

export default function VoiceDropdown() {
  const engineTTS = useRecoilValue<string>(store.engineTTS);
  const VoiceDropdownComponent = voiceDropdownComponentsMap[engineTTS];

  return <VoiceDropdownComponent />;
}
