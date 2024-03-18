import os,json
from pydub import AudioSegment
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, filtfilt, find_peaks


# Чтение  файла
def read_audio_file(filename):
    # Определяем расширение файла
    _, file_extension = os.path.splitext(filename)

    if file_extension.lower() == '.mp3':
        # Загрузка MP3 файла
        audio = AudioSegment.from_file(filename, format="mp3")
        
        # Преобразование аудио в массив numpy
        audio_data = np.array(audio.get_array_of_samples())

        # Переделываем стерео в моно при необходимости
        if audio.channels > 1:
            audio_data = audio_data.reshape((-1, audio.channels))
            audio_data = audio_data.mean(axis=1).astype(np.int16)

        sample_rate = audio.frame_rate
        
    elif file_extension.lower() == '.wav':
        # Чтение WAV файла
        sample_rate, audio_data = wavfile.read(filename)
        if audio_data.ndim > 1:
            audio_data = np.mean(audio_data, axis=1)

    else:
        raise ValueError("Unsupported file format")

    return sample_rate, audio_data

# Функция для полосового фильтра
def bandpass_filter(data, lowcut, highcut, sample_rate, order=5):
    nyquist = 0.5 * sample_rate
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    y = filtfilt(b, a, data)
    return y

# Функция для расчета средних амплитуд для заданных диапазонов
def get_amplitude_by_range(frame_data, sample_rate, freq_range):
    n = len(frame_data)
    fft_result = np.fft.rfft(frame_data)
    fft_freqs = np.fft.rfftfreq(n, 1 / sample_rate)

    amplitudes = np.abs(fft_result)

    mask = (fft_freqs >= freq_range[0]) & (fft_freqs <= freq_range[1])
    data = np.abs(amplitudes[mask])
    return data

# Функция нормализации 
def normalize(data, min_value=0, max_value=1, window_size=1, inverted = False):
    # Обрезаем выбросы, превышающие 3 стандартных отклонения
    data_mean = np.mean(data)
    data_std = np.std(data)
    data = np.clip(data, data_mean - 3 * data_std, data_mean + 3 * data_std)
    if window_size>1:
        window_size = int(window_size)
        # Паддинг - дополнение массива справа (или слева) дубликатами крайних значений
        padding = np.repeat(data[-1], window_size - 1)
        extended_array = np.concatenate((data, padding))
    
        cumsum_vec = np.cumsum(np.insert(extended_array, 0, 0)) 
        smoothed_array = (cumsum_vec[window_size:] - cumsum_vec[:-window_size]) / window_size
    
        # Обрезка массива до исходной длины
        data = smoothed_array[:len(data)]

    # Минимальное и максимальное значения для корректной нормализации
    array_min, array_max = np.min(data), np.max(data)

    # Если минимальное и максимальное значения равны, используем min_value
    if array_min == array_max:
        normalized_array = np.ones_like(data) * min_value
    else:
        # В противном случае выполняем нормализацию
        normalized_array = (data - array_min) / (array_max - array_min)
        normalized_array = normalized_array * (max_value - min_value) + min_value
    
    if inverted:
        normalized_array = max_value - (normalized_array - min_value)
    return normalized_array

def check_file_exists(filepath):
    # Получаем абсолютный путь
    absolute_path = os.path.abspath(filepath)
    
    # Проверяем существование файла
    if not os.path.isfile(absolute_path):
        return f"Файл не существует: {absolute_path}"
    return None

def generate_prompts(selected_peaks, prompts_list):
    # Очистка строк от специальных символов
    prompts_list = [prompt.replace('\n', '').replace('\r', '') for prompt in prompts_list]

    # Добавляем пустые строки, если в prompts_list меньше элементов, чем в selected_peaks
    prompts_list += [''] * (len(selected_peaks) - len(prompts_list))

    # Создаем словарь, где ключом будет строковое представление числа,
    # а значением — соответствующая строка из prompts_list
    numbers_dict = {str(peak): prompt for peak, prompt in zip(selected_peaks, prompts_list)}

    return numbers_dict

def format_peaks_to_min_sec(selected_peaks):
    # Преобразуем каждый пик в секунды
    seconds = [peak / 12 for peak in selected_peaks]
    
    # преобразовать секунды в минуты:секунды
    min_sec = [f"{int(s) // 60}:{int(s) % 60:02d}" for s in seconds]
    
    # Собираем все результаты в одну строку
    formatted_peaks_str = ', '.join([f"{ms}" for ms in min_sec])
    return formatted_peaks_str

def deforum_str(array):
    return ", ".join(f"{index}: ({value:.2f})" for index, value in enumerate(array))
        
def calculate(dm_base_settings, dm_result_settings, dm_audio,
                     dm_x_min, dm_x_max, dm_x_cad,
                     dm_y_min, dm_y_max, dm_y_cad,
                     dm_z_min, dm_z_max, dm_z_cad,
                     dm_3dX_min, dm_3dX_max, dm_3dX_cad,
                     dm_3dY_min, dm_3dY_max, dm_3dY_cad,
                     dm_3dZ_min, dm_3dZ_max, dm_3dZ_cad,
                     dm_str_min, dm_str_max, dm_str_cad,
                     dm_cfg_min, dm_cfg_max, dm_cfg_cad,
                     dm_prompt):
    # Параметры
    seconds_to_analyze = 0 # 0 - All
    frames_per_second = 12
    peaks_koef = 0.75
    human_hearing_min = 20  # Минимальная слышимая частота в Гц
    human_hearing_max = 20000  # Максимальная слышимая частота в Гц
    
    # Получаем абсолютный путь к текущей директории
    current_directory = os.path.abspath('')
    
    # Собираем полный путь к файлу настроек
    full_path = os.path.join(current_directory, dm_base_settings)

    result = check_file_exists(full_path)
    if result:
        return result

    result = check_file_exists(dm_audio)
    if result:
        return result
        
    # Чтение JSON из файла
    with open(full_path, 'r', encoding='utf-8') as f:
        deforum = json.load(f)

    sample_rate, audio_data = read_audio_file(dm_audio)
    
    # Параметры диапазонов частот
    frequency_ranges = {
        'Low Frequencies': (0, 250),
        'Mid Frequencies': (250, 2000),
        'High Frequencies': (2000, 20000),
    }

    # Применяем фильтр ко всему диапазону длины файла
    filtered_audio_data = bandpass_filter(audio_data, human_hearing_min, human_hearing_max, sample_rate)
    
    if seconds_to_analyze>0:
        audio_data = filtered_audio_data[:sample_rate * seconds_to_analyze]
    else:
        audio_data = filtered_audio_data
    
    # Подготовка массива для амплитуд по частотным диапазонам
    samples_per_frame = sample_rate // frames_per_second
    amplitudes = {range_name: [] for range_name in frequency_ranges}
    
    # Анализ амплитуд по частотным диапазонам
    # Итерируем по аудиоданным с шагом в samples_per_frame семплов
    for start in range(0, len(audio_data), samples_per_frame):
        end = start + samples_per_frame
        # Если мы на последнем сегменте и он не полный
        if end > len(audio_data):
            end = len(audio_data)  # Укорачиваем последний сегмент до конца массива
        frame_data = audio_data[start:end]
        for range_name, freq_range in frequency_ranges.items():
            amplitudes[range_name].append(
                np.mean(get_amplitude_by_range(frame_data, sample_rate, freq_range)))

    all_peaks = []
    for range_name in frequency_ranges:
        norm_array = normalize(np.array(amplitudes[range_name]),-1,1,3)
        peaks, _ = find_peaks(np.abs(np.diff(np.diff(norm_array))))
        all_peaks.extend((peak, norm_array[peak]) for peak in peaks)
    
    selected_peaks = [0]
    max_peaks = (len(audio_data) // sample_rate) // 4
    
    # Сортируем все пики по величине в убывающем порядке
    all_peaks.sort(key=lambda x: x[1], reverse=True)
    for peak, value in all_peaks:
        if not selected_peaks:
            # Если ещё нет выбранных пиков, просто добавляем первый пик
            selected_peaks.append(peak)
        else:
            # Проверяем расстояние от текущего пика до всех уже выбранных пиков
            if all(abs(peak - selected_peak) >= frames_per_second*10 for selected_peak in selected_peaks):
                selected_peaks.append(peak)
        # Если мы достигли нужного количества пиков, прерываем цикл
        if len(selected_peaks) == max_peaks:
            break
    selected_peaks.sort()
        
    format_peaks = format_peaks_to_min_sec(selected_peaks)

        
    prompts_list = dm_prompt.split("\n")
    deforum['prompts']=generate_prompts(selected_peaks, prompts_list)
    deforum['soundtrack_path']=dm_audio
    deforum['negative_prompts']= "low quality, worst quality, bad quality, lowres, bad photo, bad art, bad anatomy, bad hands, signature, text, error, cropped, jpeg artifacts, nsfw, nude"
    
    for range_name in frequency_ranges:
        if range_name == 'Low Frequencies':
            deforum['max_frames']=len(np.array(amplitudes[range_name]))
            deforum['cfg_scale_schedule'] = deforum_str(normalize(np.array(amplitudes[range_name]),dm_cfg_min,dm_cfg_max,dm_cfg_cad))
            x = normalize(np.array(amplitudes[range_name]),dm_str_min,dm_str_max,dm_str_cad,True)
            x[selected_peaks] *= peaks_koef
            deforum['strength_schedule'] = deforum_str(x)
            deforum['translation_z'] = deforum_str(normalize(np.array(amplitudes[range_name]),dm_z_min,dm_z_max,dm_z_cad))

            data_mean = np.mean(normalize(np.array(amplitudes[range_name]),dm_3dZ_min,dm_3dZ_max,dm_3dZ_cad))
            deforum['rotation_3d_z']=deforum_str(normalize(np.array(amplitudes[range_name]),dm_3dZ_min,(dm_3dZ_max-data_mean*2),dm_3dZ_cad))
        if range_name == 'Mid Frequencies':
            data_mean = np.mean(normalize(np.array(amplitudes[range_name]),dm_x_min,dm_x_max,dm_x_cad,True))
            deforum['translation_x']=deforum_str(normalize(np.array(amplitudes[range_name]),dm_x_min,(dm_x_max-data_mean*2),dm_x_cad,True))
            data_mean = np.mean(normalize(np.array(amplitudes[range_name]),dm_3dY_min,dm_3dY_max,dm_3dY_cad))
            deforum['rotation_3d_y']=deforum_str(normalize(np.array(amplitudes[range_name]),dm_3dY_min,(dm_3dY_max-data_mean*2),dm_3dY_cad))
        if range_name == 'High Frequencies':
    
            data_mean = np.mean(normalize(np.array(amplitudes[range_name]),dm_y_min,dm_y_max,dm_y_cad,True))
            deforum['translation_y']=deforum_str(normalize(np.array(amplitudes[range_name]),dm_y_min,dm_y_max-data_mean*2,dm_y_cad,True))
            
            data_mean = np.mean(normalize(np.array(amplitudes[range_name]),dm_3dX_min,dm_3dX_max,dm_3dX_cad))
            deforum['rotation_3d_x']=deforum_str(normalize(np.array(amplitudes[range_name]),dm_3dX_min,(dm_3dX_max-data_mean*2),dm_3dX_cad))

    # Сохранение файла с обновленным значением поля
    try:
        with open(dm_result_settings, 'w', encoding='utf-8') as ff:
            json.dump(deforum, ff, ensure_ascii=False, indent=4)
        print("Файл успешно обновлен.")
    except Exception as e:
        print(f"Произошла ошибка при записи файла: {e}")

    return f"Upload the settings file {dm_result_settings} to the deforum.\nSelected peaks: {format_peaks}\nBeautiful video to you."