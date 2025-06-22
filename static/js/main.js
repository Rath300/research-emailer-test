// Main JavaScript for Cold Outreach AI Matchmaker

$(document).ready(function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);

    // Smooth scrolling for anchor links
    $('a[href^="#"]').on('click', function(event) {
        var target = $(this.getAttribute('href'));
        if (target.length) {
            event.preventDefault();
            $('html, body').stop().animate({
                scrollTop: target.offset().top - 70
            }, 1000);
        }
    });

    // Form validation enhancement
    $('form').on('submit', function() {
        var $form = $(this);
        var $submitBtn = $form.find('button[type="submit"]');
        
        // Show loading state
        if ($submitBtn.length) {
            var originalText = $submitBtn.text();
            $submitBtn.prop('disabled', true);
            $submitBtn.html('<span class="spinner-border spinner-border-sm me-2"></span>Processing...');
            
            // Reset button after 10 seconds (fallback)
            setTimeout(function() {
                $submitBtn.prop('disabled', false);
                $submitBtn.text(originalText);
            }, 10000);
        }
    });

    // Copy to clipboard functionality
    $('.copy-btn').on('click', function() {
        var text = $(this).data('clipboard-text');
        navigator.clipboard.writeText(text).then(function() {
            // Show success message
            var $btn = $(this);
            var originalText = $btn.text();
            $btn.text('Copied!').addClass('btn-success').removeClass('btn-outline-secondary');
            
            setTimeout(function() {
                $btn.text(originalText).removeClass('btn-success').addClass('btn-outline-secondary');
            }, 2000);
        }.bind(this));
    });

    // Dynamic form field handling
    $('.add-field').on('click', function() {
        var $container = $(this).closest('.field-container');
        var $template = $container.find('.field-template').first();
        var $newField = $template.clone();
        
        $newField.removeClass('field-template d-none');
        $newField.find('input, textarea, select').val('');
        
        $container.find('.fields-list').append($newField);
    });

    $('.remove-field').on('click', function() {
        $(this).closest('.field-item').remove();
    });

    // File upload preview
    $('input[type="file"]').on('change', function() {
        var fileName = $(this).val().split('\\').pop();
        var $label = $(this).next('.custom-file-label');
        if ($label.length) {
            $label.text(fileName);
        }
    });

    // Search functionality
    $('.search-input').on('keyup', function() {
        var searchTerm = $(this).val().toLowerCase();
        var $items = $(this).closest('.search-container').find('.search-item');
        
        $items.each(function() {
            var text = $(this).text().toLowerCase();
            if (text.includes(searchTerm)) {
                $(this).show();
            } else {
                $(this).hide();
            }
        });
    });

    // Sort functionality
    $('.sort-select').on('change', function() {
        var sortBy = $(this).val();
        var $container = $(this).closest('.sort-container');
        var $items = $container.find('.sort-item').get();
        
        $items.sort(function(a, b) {
            var aVal = $(a).data(sortBy);
            var bVal = $(b).data(sortBy);
            
            if (aVal < bVal) return -1;
            if (aVal > bVal) return 1;
            return 0;
        });
        
        $container.find('.sort-list').empty().append($items);
    });

    // Modal enhancements
    $('.modal').on('show.bs.modal', function() {
        var $modal = $(this);
        $modal.find('.modal-body').scrollTop(0);
    });

    // Tab persistence
    $('a[data-bs-toggle="tab"]').on('shown.bs.tab', function(e) {
        localStorage.setItem('lastTab', $(e.target).attr('href'));
    });

    var lastTab = localStorage.getItem('lastTab');
    if (lastTab) {
        $('a[href="' + lastTab + '"]').tab('show');
    }

    // Progress bar animation
    $('.progress-bar').each(function() {
        var $bar = $(this);
        var percentage = $bar.attr('aria-valuenow');
        
        $bar.css('width', '0%').animate({
            width: percentage + '%'
        }, 1000);
    });

    // Match score color coding
    $('.match-score').each(function() {
        var score = parseFloat($(this).text());
        var $element = $(this);
        
        if (score >= 0.8) {
            $element.addClass('high');
        } else if (score >= 0.6) {
            $element.addClass('medium');
        } else {
            $element.addClass('low');
        }
    });

    // Email preview toggle
    $('.email-preview-toggle').on('click', function() {
        var $preview = $(this).closest('.email-item').find('.email-preview');
        $preview.slideToggle();
        
        var $icon = $(this).find('i');
        if ($icon.hasClass('fa-eye')) {
            $icon.removeClass('fa-eye').addClass('fa-eye-slash');
        } else {
            $icon.removeClass('fa-eye-slash').addClass('fa-eye');
        }
    });

    // Batch selection
    $('.batch-select-all').on('change', function() {
        var isChecked = $(this).is(':checked');
        $(this).closest('.batch-container').find('.batch-item input[type="checkbox"]').prop('checked', isChecked);
    });

    // Real-time character counter
    $('.char-counter').on('input', function() {
        var maxLength = $(this).attr('maxlength');
        var currentLength = $(this).val().length;
        var $counter = $(this).siblings('.char-counter-display');
        
        $counter.text(currentLength + '/' + maxLength);
        
        if (currentLength > maxLength * 0.9) {
            $counter.addClass('text-warning');
        } else {
            $counter.removeClass('text-warning');
        }
    });

    // Auto-save functionality
    var autoSaveTimer;
    $('.auto-save').on('input', function() {
        clearTimeout(autoSaveTimer);
        var $form = $(this).closest('form');
        
        autoSaveTimer = setTimeout(function() {
            // Show auto-save indicator
            var $indicator = $form.find('.auto-save-indicator');
            if ($indicator.length) {
                $indicator.text('Saving...').show();
                
                // Simulate auto-save (replace with actual implementation)
                setTimeout(function() {
                    $indicator.text('Saved').fadeOut();
                }, 1000);
            }
        }, 2000);
    });

    // Responsive table wrapper
    $('.table-responsive').each(function() {
        var $table = $(this);
        var $wrapper = $('<div class="table-wrapper"></div>');
        $table.wrap($wrapper);
    });

    // Loading states for buttons
    $('.btn-loading').on('click', function() {
        var $btn = $(this);
        var originalText = $btn.text();
        
        $btn.prop('disabled', true);
        $btn.html('<span class="spinner-border spinner-border-sm me-2"></span>Loading...');
        
        // Reset after 30 seconds (fallback)
        setTimeout(function() {
            $btn.prop('disabled', false);
            $btn.text(originalText);
        }, 30000);
    });

    // Toast notifications
    function showToast(message, type = 'info') {
        var toastHtml = `
            <div class="toast align-items-center text-white bg-${type} border-0" role="alert">
                <div class="d-flex">
                    <div class="toast-body">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        
        var $toast = $(toastHtml);
        $('.toast-container').append($toast);
        
        var toast = new bootstrap.Toast($toast[0]);
        toast.show();
        
        // Remove toast element after it's hidden
        $toast.on('hidden.bs.toast', function() {
            $(this).remove();
        });
    }

    // Global toast function
    window.showToast = showToast;

    // Keyboard shortcuts
    $(document).on('keydown', function(e) {
        // Ctrl/Cmd + S for save
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            $('.btn-save').click();
        }
        
        // Ctrl/Cmd + Enter for submit
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            $('form:visible button[type="submit"]').click();
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            $('.modal').modal('hide');
        }
    });

    // Performance optimization: Lazy loading for images
    $('img[data-src]').each(function() {
        var $img = $(this);
        var observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    $img.attr('src', $img.data('src'));
                    observer.unobserve($img[0]);
                }
            });
        });
        observer.observe($img[0]);
    });

    // Initialize any page-specific functionality
    if (typeof initializePage !== 'undefined') {
        initializePage();
    }
});

// Utility functions
window.utils = {
    // Format numbers with commas
    formatNumber: function(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    },
    
    // Format percentages
    formatPercentage: function(num) {
        return (num * 100).toFixed(1) + '%';
    },
    
    // Format dates
    formatDate: function(date) {
        return new Date(date).toLocaleDateString();
    },
    
    // Debounce function
    debounce: function(func, wait) {
        var timeout;
        return function executedFunction() {
            var later = function() {
                clearTimeout(timeout);
                func();
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    // Throttle function
    throttle: function(func, limit) {
        var inThrottle;
        return function() {
            var args = arguments;
            var context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(function() {
                    inThrottle = false;
                }, limit);
            }
        };
    }
}; 