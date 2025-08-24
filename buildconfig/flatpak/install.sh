flatpak remote-delete SaiyanQuestRepo
flatpak remote-add SaiyanQuestRepo SaiyanQuestRepo --no-gpg-verify --if-not-exists
flatpak install SaiyanQuestRepo org.SaiyanQuest.SaiyanQuest