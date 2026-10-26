export type ArtVariant =
  | 'living'
  | 'kitchen'
  | 'bath'
  | 'bedroom'
  | 'office'
  | 'house'
  | 'hall'
  | 'blueprint'
  | 'workshop-wood'
  | 'workshop-metal'
  | 'workshop-powder';

export const ROOM_VARIANTS: ArtVariant[] = ['living', 'kitchen', 'bath', 'bedroom', 'office', 'house'];

export const ART_LABELS: Record<ArtVariant, string> = {
  living: 'Гостиная в светлых тонах с панелями из дуба',
  kitchen: 'Кухня-гостиная в стиле лофт с металлической перегородкой',
  bath: 'Ванная комната в микроцементе',
  bedroom: 'Спальня с мягким изголовьем во всю стену',
  office: 'Офис со стеклянными перегородками',
  house: 'Интерьер частного дома с лестницей и деревянными балками',
  hall: 'Прихожая со скрытой дверью и встроенным шкафом',
  blueprint: 'Чертёж планировки квартиры',
  'workshop-wood': 'Столярный цех',
  'workshop-metal': 'Сварочный цех',
  'workshop-powder': 'Камера порошковой покраски',
};
