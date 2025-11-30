-- Подгружаем стандартные настройки звука (как было у вас)
ModRegisterAudioEventMappings( "mods/health_container/files/audio_events.txt" )

-- Функция для обновления материала в XML
function UpdateContainerMaterial()
    -- 1. Получаем выбранный материал из настроек
    local mat = ModSettingGet("health_container.container_material")
    if mat == nil then mat = "metal" end -- защита от пустого значения

    -- 2. Путь к вашему файлу предмета
    local xml_path = "mods/health_container/files/data/entities/items/pickup/health_container.xml"
    
    -- 3. Читаем содержимое файла как текст
    local content = ModTextFileGetContent(xml_path)
    
    if content ~= nil then
        -- 4. Заменяем материал. 
        -- Мы ищем pattern: material="что-угодно" и меняем на material="выбор"
        -- %a+ означает "любая последовательность букв"
        local new_content = string.gsub(content, 'material="[%w_]+"', 'material="' .. mat .. '"')
        
        -- 5. Записываем обновленный текст обратно в виртуальную память игры
        ModTextFileSetContent(xml_path, new_content)
    end
end

-- Вызываем функцию при старте мода
UpdateContainerMaterial()

-- Эта функция вызывается игрой, когда игрок меняет настройки и нажимает "ОК" (если игра не на паузе)
function OnModSettingsChanged()
    UpdateContainerMaterial()
end