import { useMemo, useState } from 'react';
import {
  ArrowDownAZ,
  CalendarDays,
  CircleDollarSign,
  Edit,
  Fuel,
  Plus,
  RotateCcw,
  Save,
  Search,
  ShieldCheck,
  Trash2,
  X,
} from 'lucide-react';
import toyotaImage from './assets/toyota-camry.jpg';
import mazdaImage from './assets/mazda-cx5.jpg';
import bmwImage from './assets/bmw-x5.jpg';

const imageOptions = [
  { value: toyotaImage, label: 'Toyota Camry' },
  { value: mazdaImage, label: 'Mazda CX-5' },
  { value: bmwImage, label: 'BMW X5' },
];

const initialCars = [
  {
    id: 1,
    title: 'Toyota Camry Premium',
    slug: 'toyota-camry-premium',
    brand: 'Toyota',
    model: 'Camry',
    year: 2025,
    price: 37500,
    body: 'Седан',
    engine: 'Бензин, 2.5 л, 203 л.с.',
    vin: 'JTDBF4E2X05012345',
    category: 'Бизнес-класс',
    tags: ['надежный', 'новый'],
    description: 'Комфортный седан для ежедневных поездок и дальних маршрутов.',
    image: toyotaImage,
    published: true,
    createdAt: '04.06.2026 15:30',
  },
  {
    id: 2,
    title: 'Mazda CX-5 Active',
    slug: 'mazda-cx-5-active',
    brand: 'Mazda',
    model: 'CX-5',
    year: 2024,
    price: 42100,
    body: 'Кроссовер',
    engine: 'Бензин, 2.0 л, 150 л.с.',
    vin: 'JM3KFBCM1R0123456',
    category: 'SUV',
    tags: ['кроссовер', 'семейный'],
    description: 'Практичный городской кроссовер с выразительным дизайном.',
    image: mazdaImage,
    published: true,
    createdAt: '03.06.2026 12:20',
  },
  {
    id: 3,
    title: 'BMW X5 xDrive',
    slug: 'bmw-x5-xdrive',
    brand: 'BMW',
    model: 'X5',
    year: 2023,
    price: 68900,
    body: 'Внедорожник',
    engine: 'Дизель, 3.0 л, 249 л.с.',
    vin: 'WBAKS410900123456',
    category: 'Премиум',
    tags: ['премиум', 'полный привод'],
    description: 'Мощный автомобиль для тех, кому важны динамика и статус.',
    image: bmwImage,
    published: true,
    createdAt: '02.06.2026 09:10',
  },
];

const emptyForm = {
  title: '',
  slug: '',
  brand: '',
  model: '',
  year: '',
  price: '',
  body: '',
  engine: '',
  vin: '',
  category: '',
  tags: '',
  description: '',
  image: toyotaImage,
  published: true,
};

const navItems = [
  { id: 'home', label: 'Главная' },
  { id: 'brands', label: 'Марки' },
  { id: 'catalog', label: 'Все автомобили' },
  { id: 'categories', label: 'Категории' },
  { id: 'tags', label: 'Теги' },
  { id: 'vin', label: 'Проверка VIN' },
  { id: 'form', label: 'Добавить авто' },
];

const sortOptions = {
  newest: 'Сначала новые',
  priceAsc: 'Цена по возрастанию',
  priceDesc: 'Цена по убыванию',
  brand: 'Марка A-Z',
  yearAsc: 'Год по возрастанию',
};

function validateCar(form, cars, editingId) {
  const errors = {};
  const vin = form.vin.trim().toUpperCase();

  if (form.title.trim().length < 5) errors.title = 'Минимум 5 символов';
  if (form.slug.trim().length < 3) errors.slug = 'Минимум 3 символа';
  if (form.brand.trim().length < 2) errors.brand = 'Введите марку';
  if (form.model.trim().length < 1) errors.model = 'Введите модель';
  if (!Number(form.year) || Number(form.year) < 1900 || Number(form.year) > 2030) {
    errors.year = 'Год должен быть от 1900 до 2030';
  }
  if (Number(form.price) < 0 || form.price === '') errors.price = 'Цена не может быть отрицательной';
  if (!form.body.trim()) errors.body = 'Укажите тип кузова';
  if (form.engine.trim().length < 5) errors.engine = 'Опишите двигатель минимум 5 символами';
  if (!form.category.trim()) errors.category = 'Укажите категорию';
  if (!/^[A-HJ-NPR-Z0-9]{17}$/i.test(vin)) errors.vin = 'VIN: 17 латинских букв/цифр без I, O, Q';
  if (cars.some((car) => car.vin === vin && car.id !== editingId)) errors.vin = 'Такой VIN уже есть';

  const tags = form.tags.split(',').map((tag) => tag.trim()).filter(Boolean);
  if (tags.length === 0) {
    errors.tags = 'Добавьте хотя бы один тег';
  } else if (tags.some((tag) => tag.length < 2)) {
    errors.tags = 'Каждый тег должен быть минимум 2 символа';
  } else if (new Set(tags.map((tag) => tag.toLowerCase())).size !== tags.length) {
    errors.tags = 'Теги не должны повторяться';
  }

  return errors;
}

function toForm(car) {
  return {
    title: car.title,
    slug: car.slug,
    brand: car.brand,
    model: car.model,
    year: String(car.year),
    price: String(car.price),
    body: car.body,
    engine: car.engine,
    vin: car.vin,
    category: car.category,
    tags: car.tags.join(', '),
    description: car.description,
    image: car.image,
    published: car.published,
  };
}

function buildCar(form, id = Date.now()) {
  return {
    id,
    title: form.title.trim(),
    slug: form.slug.trim(),
    brand: form.brand.trim(),
    model: form.model.trim(),
    year: Number(form.year),
    price: Number(form.price),
    body: form.body.trim(),
    engine: form.engine.trim(),
    vin: form.vin.trim().toUpperCase(),
    category: form.category.trim(),
    tags: form.tags.split(',').map((tag) => tag.trim()).filter(Boolean),
    description: form.description.trim() || 'Описание пока не добавлено.',
    image: form.image,
    published: form.published,
    createdAt: new Date().toLocaleString('ru-RU', { dateStyle: 'short', timeStyle: 'short' }),
  };
}

function countBy(items, key) {
  return items.reduce((acc, item) => {
    acc[item[key]] = (acc[item[key]] || 0) + 1;
    return acc;
  }, {});
}

function App() {
  const [cars, setCars] = useState(initialCars);
  const [view, setView] = useState({ type: 'home' });
  const [sortBy, setSortBy] = useState('newest');
  const [query, setQuery] = useState('');
  const [filters, setFilters] = useState({ minYear: '', maxPrice: '', body: '' });
  const [page, setPage] = useState(1);
  const [form, setForm] = useState(emptyForm);
  const [editingId, setEditingId] = useState(null);
  const [errors, setErrors] = useState({});
  const [vinInput, setVinInput] = useState('');
  const [vinResult, setVinResult] = useState(null);

  const publishedCars = cars.filter((car) => car.published);
  const selectedCar = cars.find((car) => car.id === view.carId);
  const bodyTypes = [...new Set(cars.map((car) => car.body))];

  const filteredCars = useMemo(() => {
    let prepared = publishedCars.filter((car) => {
      const searchable = `${car.title} ${car.brand} ${car.model} ${car.body} ${car.category}`.toLowerCase();
      return searchable.includes(query.toLowerCase().trim());
    });

    if (view.type === 'brand') prepared = prepared.filter((car) => car.brand === view.value);
    if (view.type === 'category') prepared = prepared.filter((car) => car.category === view.value);
    if (view.type === 'tag') prepared = prepared.filter((car) => car.tags.includes(view.value));
    if (filters.minYear) prepared = prepared.filter((car) => car.year >= Number(filters.minYear));
    if (filters.maxPrice) prepared = prepared.filter((car) => car.price <= Number(filters.maxPrice));
    if (filters.body) prepared = prepared.filter((car) => car.body === filters.body);

    return [...prepared].sort((a, b) => {
      if (sortBy === 'priceAsc') return a.price - b.price;
      if (sortBy === 'priceDesc') return b.price - a.price;
      if (sortBy === 'brand') return `${a.brand} ${a.model}`.localeCompare(`${b.brand} ${b.model}`);
      if (sortBy === 'yearAsc') return a.year - b.year;
      return b.year - a.year;
    });
  }, [cars, filters, publishedCars, query, sortBy, view]);

  const pageSize = 2;
  const totalPages = Math.max(1, Math.ceil(filteredCars.length / pageSize));
  const paginatedCars = filteredCars.slice((page - 1) * pageSize, page * pageSize);
  const averagePrice = Math.round(cars.reduce((sum, car) => sum + car.price, 0) / cars.length);

  function openView(nextView) {
    setView(nextView);
    setPage(1);
    setErrors({});
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function updateField(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
    if (errors[field]) setErrors((current) => ({ ...current, [field]: undefined }));
  }

  function submitCar(event) {
    event.preventDefault();
    const nextErrors = validateCar(form, cars, editingId);
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length > 0) return;

    if (editingId) {
      setCars((current) => current.map((car) => (car.id === editingId ? buildCar(form, editingId) : car)));
      openView({ type: 'detail', carId: editingId });
    } else {
      const car = buildCar(form);
      setCars((current) => [car, ...current]);
      openView({ type: 'detail', carId: car.id });
    }

    setForm(emptyForm);
    setEditingId(null);
  }

  function startEdit(car) {
    setForm(toForm(car));
    setEditingId(car.id);
    openView({ type: 'form' });
  }

  function deleteCar(carId) {
    setCars((current) => current.filter((car) => car.id !== carId));
    openView({ type: 'catalog' });
  }

  function cancelForm() {
    setForm(emptyForm);
    setEditingId(null);
    setErrors({});
    openView({ type: 'catalog' });
  }

  function checkVin(event) {
    event.preventDefault();
    const vin = vinInput.trim().toUpperCase();
    if (!/^[A-HJ-NPR-Z0-9]{17}$/i.test(vin)) {
      setVinResult({ error: 'VIN-код должен содержать 17 латинских букв и цифр, кроме I, O, Q' });
      return;
    }
    setVinResult({
      vin,
      wmi: vin.slice(0, 3),
      vds: vin.slice(3, 9),
      vis: vin.slice(9),
      car: cars.find((item) => item.vin === vin),
    });
  }

  function resetFilters() {
    setQuery('');
    setFilters({ minYear: '', maxPrice: '', body: '' });
    setPage(1);
  }

  return (
    <main className="app-shell">
      <Header cars={cars} averagePrice={averagePrice} view={view} openView={openView} />

      {view.type === 'home' && (
        <Home
          cars={publishedCars.slice(0, 4)}
          openView={openView}
        />
      )}

      {['catalog', 'brand', 'category', 'tag'].includes(view.type) && (
        <Catalog
          title={viewTitle(view)}
          cars={paginatedCars}
          total={filteredCars.length}
          page={page}
          totalPages={totalPages}
          setPage={setPage}
          query={query}
          setQuery={setQuery}
          sortBy={sortBy}
          setSortBy={setSortBy}
          filters={filters}
          setFilters={setFilters}
          bodyTypes={bodyTypes}
          resetFilters={resetFilters}
          openView={openView}
        />
      )}

      {view.type === 'brands' && <Directory title="Все марки автомобилей" items={directory(cars, 'brand')} kind="brand" openView={openView} />}
      {view.type === 'categories' && <Directory title="Все категории" items={directory(cars, 'category')} kind="category" openView={openView} />}
      {view.type === 'tags' && <Directory title="Все теги" items={tagDirectory(cars)} kind="tag" openView={openView} />}

      {view.type === 'detail' && selectedCar && (
        <Detail car={selectedCar} openView={openView} startEdit={startEdit} deleteCar={deleteCar} />
      )}

      {view.type === 'form' && (
        <CarForm
          form={form}
          errors={errors}
          editingId={editingId}
          updateField={updateField}
          submitCar={submitCar}
          cancelForm={cancelForm}
        />
      )}

      {view.type === 'vin' && (
        <VinCheck vinInput={vinInput} setVinInput={setVinInput} vinResult={vinResult} checkVin={checkVin} openView={openView} />
      )}
    </main>
  );
}

function Header({ cars, averagePrice, view, openView }) {
  return (
    <>
      <section className="toolbar">
        <div>
          <h1>Автомобильный каталог</h1>
        </div>
        <div className="stats">
          <Stat label="Всего авто" value={cars.length} />
          <Stat label="Средняя цена" value={`$${averagePrice.toLocaleString('ru-RU')}`} />
          <Stat label="Новых от 2024" value={cars.filter((car) => car.year >= 2024).length} />
        </div>
      </section>
      <nav className="main-nav">
        {navItems.map((item) => (
          <button
            key={item.id}
            className={view.type === item.id ? 'active' : ''}
            type="button"
            onClick={() => openView({ type: item.id })}
          >
            {item.label}
          </button>
        ))}
      </nav>
    </>
  );
}

function Home({ cars, openView }) {
  return (
    <section>
      <div className="section-heading">
        <div>
          <h2>Главная страница</h2>
          <p>Добро пожаловать в каталог автомобилей</p>
        </div>
        <button className="ghost-button" type="button" onClick={() => openView({ type: 'catalog' })}>
          Все автомобили
        </button>
      </div>
      <CarsGrid cars={cars} openView={openView} />
    </section>
  );
}

function Catalog(props) {
  const {
    title,
    cars,
    total,
    page,
    totalPages,
    setPage,
    query,
    setQuery,
    sortBy,
    setSortBy,
    filters,
    setFilters,
    bodyTypes,
    resetFilters,
    openView,
  } = props;

  return (
    <section className="catalog-layout">
      <aside className="controls-panel">
        <Control label="Поиск" icon={<Search size={18} />}>
          <input value={query} placeholder="Марка, модель, категория" onChange={(event) => setQuery(event.target.value)} />
        </Control>
        <Control label="Сортировка" icon={<ArrowDownAZ size={18} />}>
          <select value={sortBy} onChange={(event) => setSortBy(event.target.value)}>
            {Object.entries(sortOptions).map(([value, label]) => (
              <option key={value} value={value}>{label}</option>
            ))}
          </select>
        </Control>
        <Control label="Год от">
          <input
            type="number"
            placeholder="2020"
            value={filters.minYear}
            onChange={(event) => setFilters((current) => ({ ...current, minYear: event.target.value }))}
          />
        </Control>
        <Control label="Цена до">
          <input
            type="number"
            placeholder="50000"
            value={filters.maxPrice}
            onChange={(event) => setFilters((current) => ({ ...current, maxPrice: event.target.value }))}
          />
        </Control>
        <Control label="Тип кузова">
          <select
            value={filters.body}
            onChange={(event) => setFilters((current) => ({ ...current, body: event.target.value }))}
          >
            <option value="">Все</option>
            {bodyTypes.map((body) => <option key={body} value={body}>{body}</option>)}
          </select>
        </Control>
        <button className="ghost-button" type="button" onClick={resetFilters}>
          <RotateCcw size={18} />
          Сбросить
        </button>
      </aside>

      <section className="cars-area">
        <div className="section-heading">
          <h2>{title}</h2>
          <span>{total} найдено</span>
        </div>
        <CarsGrid cars={cars} openView={openView} />
        <Pagination page={page} totalPages={totalPages} setPage={setPage} />
      </section>
    </section>
  );
}

function CarsGrid({ cars, openView }) {
  if (cars.length === 0) return <p className="empty">Автомобили не найдены.</p>;

  return (
    <div className="cars-grid">
      {cars.map((car) => (
        <article className="car-card" key={car.id}>
          <button className="image-button" type="button" onClick={() => openView({ type: 'detail', carId: car.id })}>
            <img src={car.image} alt={`${car.brand} ${car.model}`} />
          </button>
          <div className="car-card-body">
            <p className="car-category">{car.category}</p>
            <h3>{car.brand} {car.model}</h3>
            <p>{car.description}</p>
            <div className="car-meta">
              <span><CalendarDays size={16} />{car.year}</span>
              <span><CircleDollarSign size={16} />${car.price.toLocaleString('ru-RU')}</span>
              <span><Fuel size={16} />{car.body}</span>
            </div>
            <button className="ghost-button" type="button" onClick={() => openView({ type: 'detail', carId: car.id })}>
              Подробнее
            </button>
          </div>
        </article>
      ))}
    </div>
  );
}

function Directory({ title, items, kind, openView }) {
  return (
    <section>
      <div className="section-heading"><h2>{title}</h2><span>{items.length} записей</span></div>
      <div className="directory-grid">
        {items.map((item) => (
          <button
            className="directory-card"
            key={item.name}
            type="button"
            onClick={() => openView({ type: kind, value: item.name })}
          >
            <strong>{kind === 'tag' ? `#${item.name}` : item.name}</strong>
            <span>Автомобилей: {item.count}</span>
            <small>Смотреть все</small>
          </button>
        ))}
      </div>
    </section>
  );
}

function Detail({ car, openView, startEdit, deleteCar }) {
  return (
    <article className="detail">
      <button className="ghost-button back-button" type="button" onClick={() => openView({ type: 'catalog' })}>Назад к списку</button>
      <img src={car.image} alt={`${car.brand} ${car.model}`} />
      <div className="detail-info">
        <p className="car-category">{car.category}</p>
        <h2>{car.brand} {car.model}</h2>
        <p>{car.description}</p>
        <dl>
          <div><dt>Название</dt><dd>{car.title}</dd></div>
          <div><dt>Год выпуска</dt><dd>{car.year}</dd></div>
          <div><dt>Тип кузова</dt><dd>{car.body}</dd></div>
          <div><dt>Цена</dt><dd>${car.price.toLocaleString('ru-RU')}</dd></div>
          <div><dt>VIN</dt><dd>{car.vin}</dd></div>
          <div><dt>Двигатель</dt><dd>{car.engine}</dd></div>
          <div><dt>Добавлено</dt><dd>{car.createdAt}</dd></div>
        </dl>
        <div className="tags">
          {car.tags.map((tag) => <span key={`${car.id}-${tag}`}>{tag}</span>)}
        </div>
        <div className="action-row">
          <button className="ghost-button" type="button" onClick={() => startEdit(car)}><Edit size={18} />Редактировать</button>
          <button className="danger-button" type="button" onClick={() => deleteCar(car.id)}><Trash2 size={18} />Удалить</button>
        </div>
      </div>
    </article>
  );
}

function CarForm({ form, errors, editingId, updateField, submitCar, cancelForm }) {
  return (
    <section className="form-section">
      <div className="section-heading">
        <h2>{editingId ? 'Редактирование автомобиля' : 'Добавить автомобиль'}</h2>
        <span>Форма работает без бэкенда, через состояние React</span>
      </div>
      <form className="car-form" onSubmit={submitCar} noValidate>
        <Field label="Название" name="title" value={form.title} error={errors.title} onChange={updateField} />
        <Field label="URL-слаг" name="slug" value={form.slug} error={errors.slug} onChange={updateField} />
        <Field label="Марка" name="brand" value={form.brand} error={errors.brand} onChange={updateField} />
        <Field label="Модель" name="model" value={form.model} error={errors.model} onChange={updateField} />
        <Field label="Год выпуска" name="year" type="number" value={form.year} error={errors.year} onChange={updateField} />
        <Field label="Цена, $" name="price" type="number" value={form.price} error={errors.price} onChange={updateField} />
        <Field label="Кузов" name="body" value={form.body} error={errors.body} onChange={updateField} />
        <Field label="Двигатель" name="engine" value={form.engine} error={errors.engine} onChange={updateField} />
        <Field label="VIN" name="vin" value={form.vin} error={errors.vin} onChange={updateField} />
        <Field label="Категория" name="category" value={form.category} error={errors.category} onChange={updateField} />
        <Field label="Теги через запятую" name="tags" value={form.tags} error={errors.tags} onChange={updateField} />
        <label className="field">
          <span>Фото</span>
          <select value={form.image} onChange={(event) => updateField('image', event.target.value)}>
            {imageOptions.map((image) => <option key={image.label} value={image.value}>{image.label}</option>)}
          </select>
        </label>
        <label className="field checkbox-field">
          <input type="checkbox" checked={form.published} onChange={(event) => updateField('published', event.target.checked)} />
          <span>Опубликовано</span>
        </label>
        <label className={`field wide ${errors.description ? 'field-error' : ''}`}>
          <span>Описание</span>
          <textarea value={form.description} rows="4" onChange={(event) => updateField('description', event.target.value)} />
          {errors.description && <small>{errors.description}</small>}
        </label>
        <button className="submit-button" type="submit"><Save size={18} />{editingId ? 'Сохранить' : 'Добавить'}</button>
        <button className="ghost-button" type="button" onClick={cancelForm}><X size={18} />Отмена</button>
      </form>
    </section>
  );
}

function VinCheck({ vinInput, setVinInput, vinResult, checkVin, openView }) {
  return (
    <section>
      <div className="section-heading"><h2>Проверка VIN-кода</h2><span>Фронтенд-аналог страницы VIN</span></div>
      <form className="vin-form" onSubmit={checkVin}>
        <input value={vinInput} maxLength="17" placeholder="Например: JTDBF4E2X05012345" onChange={(event) => setVinInput(event.target.value)} />
        <button className="submit-button" type="submit"><ShieldCheck size={18} />Проверить VIN</button>
      </form>
      {vinResult?.error && <p className="form-error">{vinResult.error}</p>}
      {vinResult?.vin && (
        <div className="vin-block">
          <p><b>VIN:</b> {vinResult.vin}</p>
          <p><b>WMI:</b> {vinResult.wmi}</p>
          <p><b>VDS:</b> {vinResult.vds}</p>
          <p><b>VIS:</b> {vinResult.vis}</p>
          {vinResult.car ? (
            <button className="ghost-button" type="button" onClick={() => openView({ type: 'detail', carId: vinResult.car.id })}>
              Автомобиль найден: {vinResult.car.brand} {vinResult.car.model}
            </button>
          ) : <p>Автомобиль с таким VIN не найден.</p>}
        </div>
      )}
    </section>
  );
}

function Field({ label, name, value, type = 'text', error, onChange }) {
  return (
    <label className={`field ${error ? 'field-error' : ''}`}>
      <span>{label}</span>
      <input type={type} value={value} onChange={(event) => onChange(name, event.target.value)} />
      {error && <small>{error}</small>}
    </label>
  );
}

function Control({ label, icon, children }) {
  return (
    <div className="control-row">
      <label>{icon}{label}</label>
      {children}
    </div>
  );
}

function Pagination({ page, totalPages, setPage }) {
  if (totalPages < 2) return null;

  return (
    <nav className="list-pages">
      <button type="button" disabled={page === 1} onClick={() => setPage(page - 1)}>&lt;</button>
      {Array.from({ length: totalPages }, (_, index) => index + 1).map((number) => (
        <button
          key={number}
          className={page === number ? 'page-num-selected' : ''}
          type="button"
          onClick={() => setPage(number)}
        >
          {number}
        </button>
      ))}
      <button type="button" disabled={page === totalPages} onClick={() => setPage(page + 1)}>&gt;</button>
    </nav>
  );
}

function Stat({ label, value }) {
  return (
    <div className="stat">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function directory(cars, key) {
  const counts = countBy(cars.filter((car) => car.published), key);
  return Object.entries(counts).map(([name, count]) => ({ name, count })).sort((a, b) => a.name.localeCompare(b.name));
}

function tagDirectory(cars) {
  const counts = cars.filter((car) => car.published).flatMap((car) => car.tags).reduce((acc, tag) => {
    acc[tag] = (acc[tag] || 0) + 1;
    return acc;
  }, {});
  return Object.entries(counts).map(([name, count]) => ({ name, count })).sort((a, b) => a.name.localeCompare(b.name));
}

function viewTitle(view) {
  if (view.type === 'brand') return `Автомобили марки ${view.value}`;
  if (view.type === 'category') return `Категория: ${view.value}`;
  if (view.type === 'tag') return `Тег: ${view.value}`;
  return 'Список всех автомобилей';
}

export default App;
